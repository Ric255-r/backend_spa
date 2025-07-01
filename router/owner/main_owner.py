from datetime import datetime
import os
import stat
from typing import Optional
import uuid
import aiomysql
from fastapi import APIRouter, File, Form, Query, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.cell import MergedCell
from openpyxl.workbook.protection import WorkbookProtection
import pandas as pd
from aiomysql import Error as aiomysqlerror
import asyncio
import win32com.client
from pywintypes import com_error

app = APIRouter(prefix=("/main_owner"))

@app.get('/get_laporan')
async def getLaporan() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # Pilih Awal dlu
        qMain = "SELECT id_transaksi, disc, gtotal_stlh_pajak, total_harga, jenis_pembayaran FROM main_transaksi WHERE status IN ('paid', 'done') AND is_cancel = 0"
        await cursor.execute(qMain)  
        itemMain = await cursor.fetchall()

        # Buat dictionary main_transaksi
        main_trans_dict = {item['id_transaksi']: item for item in itemMain}
        """
          hasil main_trans_dict : 
          {
            "TF0001": {
              "id_transaksi": "TF0001",
              "disc": 0.2,
              "gtotal_stlh_pajak": 648000,
              "total_harga": 810000
            },
            "TF0002": { dan seterusnya},
          }
        """

        """
          Fungsi Query1 Ini : (Utk Line Chart)
          1. Filters records where created_at is from the first day of the current month
          2. Up to (but not including) the first day of the month 12 months from now
          3. Groups by year-month
          4. Orders chronologically
          5. Limits to 12 months of results
        """
        # q1 = """

        #   SELECT DATE_FORMAT(created_at, "%Y-%m") AS bulan,
        #   SUM(gtotal_stlh_pajak) AS omset_jual
        #   FROM main_transaksi
        #   WHERE created_at >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01') 
        #   AND created_at < DATE_FORMAT(DATE_ADD(CURRENT_DATE, INTERVAL 12 MONTH), '%Y-%m-01')
        #   GROUP BY bulan
        #   LIMIT 12
        # """
        q1 = """
          WITH RECURSIVE months AS (
            SELECT DATE_FORMAT(DATE_SUB(CURRENT_DATE, INTERVAL 11 MONTH), '%Y-%m') AS bulan,
            1 AS num
            UNION ALL
            SELECT DATE_FORMAT(DATE_ADD(DATE_SUB(CURRENT_DATE, INTERVAL 11 MONTH), INTERVAL num MONTH), '%Y-%m'), num + 1
            FROM months 
            WHERE num < 12
          )
          SELECT m.bulan, IFNULL(SUM(t.gtotal_stlh_pajak), 0) AS omset_jual
          FROM months m 
          LEFT JOIN main_transaksi t 
          ON DATE_FORMAT(t.created_at, '%Y-%m') = m.bulan AND t.status IN ('done', 'paid') AND t.is_cancel = 0
          GROUP BY m.bulan
          ORDER BY m.bulan
        """
        await cursor.execute(q1)  
        items1 = await cursor.fetchall()

        # Utk Perbandingan Current Month sama Sebelumnya. Total Penjualan (Paket Produk)
        queryWith = """
          WITH months AS (
            SELECT DATE_FORMAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 MONTH), '%Y-%m') AS bulan
            UNION ALL
            SELECT DATE_FORMAT(CURRENT_DATE, '%Y-%m') AS bulan
          )
        """
        # Utk Dapetin Monthly Sales
        q2 = f"""
          {queryWith}
          SELECT m.bulan, IFNULL(SUM(t.gtotal_stlh_pajak), 0) AS omset_jual
          FROM months m
          LEFT JOIN main_transaksi t 
            ON DATE_FORMAT(t.created_at, '%Y-%m') = m.bulan 
            AND t.is_cancel = 0

          GROUP BY m.bulan
          ORDER BY m.bulan DESC
        """
        await cursor.execute(q2)
        items2 = await cursor.fetchall()

        # Penjualan Paket. ambil dari gtotal_stlh_pajak yg main_transaksi. 
        q3 = f"""
          {queryWith}
          SELECT 
              m.bulan, 
              IFNULL(SUM(dtp.harga_total), 0) AS omset_jual_paket,
              t.id_transaksi, dtp.is_addon, t.jenis_pembayaran
          FROM 
              months m
          LEFT JOIN 
              main_transaksi t ON DATE_FORMAT(t.created_at, '%Y-%m') = m.bulan
              AND t.status IN ('paid', 'done')  -- Only count completed transactions
              AND t.is_cancel = 0
          LEFT JOIN 
              detail_transaksi_paket dtp ON t.id_transaksi = dtp.id_transaksi
              AND dtp.status = 'paid'  -- Only count paid package items
              AND dtp.is_returned = 0  -- Exclude returned items
          GROUP BY 
              m.bulan, t.id_transaksi, dtp.is_addon, t.jenis_pembayaran
          ORDER BY 
              m.bulan DESC
        """
        await cursor.execute(q3)
        items3 = await cursor.fetchall()

        penjualan_paket = []
        for data in items3:
          id_transaksi = data['id_transaksi']
          omset_jual_paket = int(data['omset_jual_paket']) or 0

          # ambil key id_transaksi di maintrans yg sama dgn data['id_transaksi']
          get_same_id = main_trans_dict.get(id_transaksi, {}) #klo g ad return obj kosong
          disc = float(get_same_id.get('disc', 0)) #klo g ad maka 0
          
          # Rumus Persen
          # if data['jenis_pembayaran'] == 1:
          #   # Case 1: Bayar diakhir, pasti dpt disc
          #   nominal_disc = omset_jual_paket * disc
          #   harga_stlh_disc = omset_jual_paket - nominal_disc
          # elif data['jenis_pembayaran'] == 0 and data['is_addon'] == 0:
          #   # Case 2: Payment upfront - only apply discount to non-addon items
          #   nominal_disc = omset_jual_paket * disc
          #   harga_stlh_disc = omset_jual_paket - nominal_disc
          # else:
          #   # Ga dpt disc (bayar diawal. addon g dpt)
          #   harga_stlh_disc = omset_jual_paket

          # Update key items3
          data['omset_jual_paket'] = omset_jual_paket
          penjualan_paket.append(data)

        # GroupBy valuenya berdasarkan key bulan
        monthly_paket = {}
        for entry in penjualan_paket:
          bulan = entry['bulan']
          if bulan in monthly_paket:
            monthly_paket[bulan] += entry['omset_jual_paket']
          else:
            monthly_paket[bulan] = entry['omset_jual_paket']

        # restruktur ulang dictionarynya, lalujadikan dataframe biar bentuk kek tabel sql
        monthly_paket_df = {'bulan': list(monthly_paket.keys()), 'omset_bulanan': list(monthly_paket.values())}
        df_paket = pd.DataFrame(monthly_paket_df)
        # End Penjualan Paket

        q4 = f"""
          {queryWith}
          SELECT m.bulan, IFNULL(SUM(dtp.harga_total), 0) AS omset_jual_produk, t.id_transaksi,
          dtp.is_addon, t.jenis_pembayaran
          FROM months m
          -- pakai left join lalu and ke main_transaksi
          LEFT JOIN main_transaksi t 
            ON DATE_FORMAT(t.created_at, '%Y-%m') = m.bulan 
            AND t.status IN ('paid', 'done') 
            AND t.is_cancel = 0
          -- pakai left join lalu and ke detail_trans
          LEFT JOIN detail_transaksi_produk dtp 
            ON t.id_transaksi = dtp.id_transaksi 
            AND dtp.status = 'paid'
          -- baru digroup by
          GROUP BY m.bulan, t.id_transaksi, dtp.is_addon, t.jenis_pembayaran
          ORDER BY m.bulan DESC
        """
        await cursor.execute(q4)
        items4 = await cursor.fetchall()

        # Buat list dlu supaya bs update data baru
        list_produk = []
        for data in items4:
          id_transaksi = data['id_transaksi']
          omset_jual_produk = int(data['omset_jual_produk']) or 0

          # ambil key maintrans yg sama dgn id_transaksi omset_jual_produk
          get_same_id = main_trans_dict.get(id_transaksi, {})
          disc = get_same_id.get('disc', 0)

          # Rumus Persen
          # if data['jenis_pembayaran'] == 1:
          #   # Case 1, Bayar Akhir, pasti dpt disc
          #   nominal_disc = omset_jual_produk * disc
          #   harga_stlh_disc = omset_jual_produk - nominal_disc
          # elif data['jenis_pembayaran'] == 0 and data['is_addon'] == 0:
          #   # Case 2: Payment upfront - only apply discount to non-addon items
          #   nominal_disc = omset_jual_produk * disc
          #   harga_stlh_disc = omset_jual_produk - nominal_disc
          # else:
          #   # Case 3: No discount applies (upfront payment for addon items)
          #   harga_stlh_disc = omset_jual_produk

          # Update key items3
          data['omset_jual_produk'] = omset_jual_produk
          list_produk.append(data)
        
        # Groupby Valuenya berdasarkan bulan
        monthly_produk = {}
        for item in list_produk:
          bulan = item['bulan']
          if bulan in monthly_produk:
            monthly_produk[bulan] += item['omset_jual_produk']
          else:
            monthly_produk[bulan] = item['omset_jual_produk']

        # Restruktur ulang dictionarynya lalu jadikan dataframe supaya membentuk kek sql
        monthly_produk_df = {'bulan': list(monthly_produk.keys()), 'omset_bulanan': list(monthly_produk.values())}
        df_produk = pd.DataFrame(monthly_produk_df) 

        # cek paket populer
        q5 = """
          SELECT 
            p.nama_paket_msg AS label,
            COUNT(*) AS jumlah_terjual
          FROM detail_transaksi_paket d
          JOIN paket_massage p ON d.id_paket = p.id_paket_msg
          WHERE d.status = 'paid'
            AND d.is_returned = 0
          GROUP BY d.id_paket
          ORDER BY jumlah_terjual DESC
          LIMIT 4;
        """
        await cursor.execute(q5)
        items5 = await cursor.fetchall()
        
        return {
          "for_line_chart" : items1,
          "monthly_sales": items2,
          "sum_paket": df_paket.to_dict('records'),
          "sum_produk": df_produk.to_dict('records'),
          "paket_terlaris": items5
        }

  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code) 
  
def excel_to_pdf(excel_path, pdf_path):
  excel = win32com.client.Dispatch("Excel.Application")
  excel.Visible = False #Buat Excel Hidden
  excel.DisplayAlerts = False #Lewati Alert

  try:
    print(f"Converting '{excel_path}' to PDF...")
    wb = excel.Workbooks.Open(os.path.abspath(excel_path))
    # --- Add Page Setup to fit content ---
    ws = wb.ActiveSheet
    # --- Page Setup Configuration ---
    # 1. Set print area to only used cells
    used_range = ws.UsedRange
    ws.PageSetup.PrintArea = used_range.Address
    
    # 2. Fit to one page wide and tall
    ws.PageSetup.FitToPagesWide = 1
    ws.PageSetup.FitToPagesTall = 1
    
    # 3. Prevent row/column splitting
    ws.PageSetup.FitToPagesTall = False  # Allow multiple pages if needed
    ws.PageSetup.Zoom = False  # Disable zoom to enforce FitToPages
    
    # 4. Set margins (optional, adjust as needed)
    ws.PageSetup.LeftMargin = 20
    ws.PageSetup.RightMargin = 20
    ws.PageSetup.TopMargin = 20
    ws.PageSetup.BottomMargin = 20
    
    # 5. Center on page
    ws.PageSetup.CenterHorizontally = True
    ws.PageSetup.CenterVertically = True
    
    # 6. Set paper size (A4)
    ws.PageSetup.PaperSize = 9  # 9 = xlPaperA4
    
    # 7. Set orientation (Auto: Excel will decide based on content)
    if used_range.Columns.Count > 10:  # If many columns, use landscape
        ws.PageSetup.Orientation = 2  # 2 = xlLandscape
    else:
        ws.PageSetup.Orientation = 1  # 1 = xlPortrait

    # --- Export to PDF ---
    wb.ActiveSheet.ExportAsFixedFormat(0, os.path.abspath(pdf_path))
    print("Conversion successful!")
        
  except com_error as e:
    print(f"Conversion failed: {e}")
  finally:
    if 'wb' in locals() and wb:
      wb.Close(SaveChanges=False)
    if excel:
      excel.Quit()
  
@app.get('/export_excel')
async def exportExcel(
  start_date: Optional[str] = Query(None),
  end_date: Optional[str] = Query(None)
):
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

          kondisi = ""
          tgl = ""
          params= []
          if start_date and end_date:
            tgl = start_date + " s/d " + end_date
            kondisi = "WHERE DATE(mt.created_at) BETWEEN %s AND %s"
            params.extend([start_date, end_date])
          elif start_date:
            tgl = start_date
            kondisi = "WHERE DATE(mt.created_at) = %s"
            params.append(start_date)            
          else:
            kondisi = "WHERE DATE(mt.created_at) = CURDATE()"
            # Ambil Date Now Skrg
            q_tgl = "SELECT NOW() AS tgl"
            await cursor.execute(q_tgl)

            item_tgl = await cursor.fetchone()
            tgl = item_tgl['tgl']

          q1 = f"""
            SELECT mt.id_transaksi,  mt.no_loker, mt.created_at AS tgl_beli, mt.jenis_transaksi, mt.jenis_tamu, mt.id_member, 
            k.nama_karyawan as resepsionis,
            mt.total_harga, mt.disc, mt.grand_total, mt.metode_pembayaran as metode_bayar
            FROM main_transaksi mt
            LEFT JOIN karyawan k ON mt.id_resepsionis = k.id_karyawan
            LEFT JOIN karyawan k_terapis ON mt.id_terapis = k_terapis.id_karyawan
            LEFT JOIN karyawan k_gro ON mt.id_gro = k_gro.id_karyawan {kondisi}
          """
          await cursor.execute(q1, params)
          main_data = await cursor.fetchall()

          # Step 2, buat Workbook Excel. wb = WorkBook, ws = WorkSheet
          wb = Workbook()
          ws = wb.active
          ws.title = "Transaksi All"

          # Step 3, Tambahkan Header kaya Judul lalu di Merge
          corporate_name = "PLATINUM"
          ws.merge_cells('A1:K1') # Merge A1 smpe M1
          corp_cell = ws['A1']
          corp_cell.value = corporate_name

          # Step 4, Center Text Corporate Name
          corp_cell.alignment = Alignment(horizontal='center', vertical='center')
          header_font = Font(bold=True, size=18)
          for cell in ws[1]:# index row excel start dr 1. ini ceritany mw tebalin PLATINUM
            cell.font = header_font

          # Step 5, Tambah Keterangan dibawah nama korporat yg diheader A1
          corporate_ket = f"LAPORAN PENJUALAN PER TANGGAL {tgl}"
          ws.merge_cells('A2:K2')
          ket_cell = ws['A2']
          ket_cell.value = corporate_ket

          # Step 6. Center Tulisan LapPenjualan
          ket_cell.alignment = Alignment(horizontal='center', vertical='center')
          header2_font = Font(bold=True, size=15)
          for cell in ws[2]:
            cell.font = header2_font

          # Buat Row Kosong
          ws.append([])

          # Step 7 : Tambah Header. konversi ke string dlu
          column_main = []
          for col in main_data[0].keys():
            replaced_str = str(col).capitalize().replace("_", " ")
            column_main.append(replaced_str)

          ws.append(column_main)

          # Step 7.5 Desain Header. ws itu adalah worksheet row ke 4
          header_row = ws[4] # Diambil dari row ke 4 yg udh di append pada step 7.5
          for cell in header_row:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = PatternFill(start_color="D3D3D3", fill_type="solid")
            cell.border = Border(
              left=Side(style="thin"),
              right=Side(style="thin"),
              top=Side(style="thin"),
              bottom=Side(style="thin"),
            )

          # Step 8 : Tambah data ke ws. jadikan list dlu, br ambil values
          for row in main_data:
            row_as_str = []
            for value in row.values():
              if isinstance(value, datetime):
                value = value.strftime('%d-%m-%Y\n%H:%M:%S')
              elif isinstance(value, int):
                value = value
              elif isinstance(value, float):
                value = str(value).replace("0.", "")
                if value == "0":
                  value = "-"
                else:
                  value += "0%"

              elif value == "" or not value:
                value = "-"
              else:
                value = str(value)
              
              row_as_str.append(value)
            print(row_as_str)
            ws.append(row_as_str)

            # Step 8.5: Tambahkan border ke setiap row
            thin_border = Border(
              bottom=Side(style='thin')
            )
            
            for row in ws.iter_rows(min_row=5, max_row=ws.max_row):  # Mulai dari row 5 (data pertama setelah header)
              for cell in row:
                cell.border = thin_border

          # Step 9 : Auto Adjust Column width berdasarkan konten
          for idx, col in enumerate(ws.columns, 1):  # Mulai dari 1 (kolom A)
            column_letter = get_column_letter(idx)
            max_length = 0
            
            for cell in col:
              # Lewati looping yg mergedcell
              if isinstance(cell, MergedCell):
                continue
              
              try:
                # Handle khusus untuk teks yang ada newline
                cell_value = str(cell.value)

                # Penanganan khusus untuk kolom id_transaksi (kolom pertama)
                if idx == 1:  # Kolom A (id_transaksi)
                  # Tetapkan panjang maksimum 8 karakter untuk id_transaksi
                  max_length = 8
                  break  # Keluar dari loop karena kita sudah tetapkan manual

                elif "\n" in cell_value:
                  # ambil line terpanjang
                  line_lengths = [len(line) for line in cell_value.split("\n")]
                  cell_length = max(line_lengths)
                else:
                  # buat lebar cell berdasarkan panjang data
                  cell_length = len(cell_value)

                if cell_length > max_length:
                  max_length = len(str(cell.value))
              except:
                pass
            
            if idx == 1:
              # Khusus id_transaksi ttpin 10 karakter
              adjusted_width = 15
            elif idx == 3:
              # Tglbeli, 12 karakter aja
              adjusted_width = 12
            else:
              # Kasih Buffer 20% dan minimum width 5
              adjusted_width = max((max_length + 2) * 1.2, 5)

            ws.column_dimensions[column_letter].width = adjusted_width

            # aktifkan wraptext untuk kolom yang ada newline
            for cell in col:
              if cell.value and "\n" in str(cell.value):
                cell.alignment = Alignment(wrap_text=True)

          # Step 10 : Simpan Workbook Ke File
          file_path = "datapenjualan_platinum.xlsx"
          # Temporarily Make File Writable Before Overwriting
          if os.path.exists(file_path):
            os.chmod(file_path, 0o644)  # Grant write permissions (rw-r--r--)

          wb.save(file_path)
          os.chmod(file_path, 0o444)  # Set back to read-only

          pdf_output = "datapenjualan_platinum.pdf"
          excel_to_pdf(file_path, pdf_output)

          await asyncio.sleep(1.0)

          # Step 11. Return Excelny sbg FileResponse
          return FileResponse(
            os.path.abspath("datapenjualan_platinum.pdf"),
            media_type='application/pdf',
            filename="datapenjualan_platinum.pdf"
          )

        except aiomysqlerror as e:
          return JSONResponse({"Error": f"Sql Error {str(e)}"}, status_code=500)
        except HTTPException as e:
          return JSONResponse({"Error": f"HTTP Error {str(e.detail)}"}, status_code=e.status_code)
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)

