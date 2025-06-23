import os
import stat
from typing import Optional
import uuid
import aiomysql
from fastapi import APIRouter, File, Form, Query, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.workbook.protection import WorkbookProtection
import pandas as pd
from aiomysql import Error as aiomysqlerror
import asyncio

app = APIRouter(prefix=("/main_owner"))

@app.get('/get_laporan')
async def getLaporan() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # Pilih Awal dlu
        qMain = "SELECT id_transaksi, disc, grand_total, total_harga, jenis_pembayaran FROM main_transaksi WHERE status IN ('paid', 'done') AND is_cancel = 0"
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
              "grand_total": 648000,
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
        #   SUM(grand_total) AS omset_jual
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
          SELECT m.bulan, IFNULL(SUM(t.grand_total), 0) AS omset_jual
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
          SELECT m.bulan, IFNULL(SUM(t.grand_total), 0) AS omset_jual
          FROM months m
          LEFT JOIN main_transaksi t ON DATE_FORMAT(t.created_at, '%Y-%m') = m.bulan AND t.is_cancel = 0

          GROUP BY m.bulan
          ORDER BY m.bulan DESC
        """
        await cursor.execute(q2)
        items2 = await cursor.fetchall()

        # Penjualan Paket. ambil dari grand_total yg main_transaksi. 
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
          if data['jenis_pembayaran'] == 1:
            # Case 1: Bayar diakhir, pasti dpt disc
            nominal_disc = omset_jual_paket * disc
            harga_stlh_disc = omset_jual_paket - nominal_disc
          elif data['jenis_pembayaran'] == 0 and data['is_addon'] == 0:
            # Case 2: Payment upfront - only apply discount to non-addon items
            nominal_disc = omset_jual_paket * disc
            harga_stlh_disc = omset_jual_paket - nominal_disc
          else:
            # Ga dpt disc (bayar diawal. addon g dpt)
            harga_stlh_disc = omset_jual_paket

          # Update key items3
          data['omset_jual_paket'] = harga_stlh_disc
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
          ON DATE_FORMAT(t.created_at, '%Y-%m') = m.bulan AND t.status IN ('paid', 'done') AND t.is_cancel = 0
          -- pakai left join lalu and ke detail_trans
          LEFT JOIN detail_transaksi_produk dtp 
          ON t.id_transaksi = dtp.id_transaksi AND dtp.status = 'paid'
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
          if data['jenis_pembayaran'] == 1:
            # Case 1, Bayar Akhir, pasti dpt disc
            nominal_disc = omset_jual_produk * disc
            harga_stlh_disc = omset_jual_produk - nominal_disc
          elif data['jenis_pembayaran'] == 0 and data['is_addon'] == 0:
            # Case 2: Payment upfront - only apply discount to non-addon items
            nominal_disc = omset_jual_produk * disc
            harga_stlh_disc = omset_jual_produk - nominal_disc
          else:
            # Case 3: No discount applies (upfront payment for addon items)
            harga_stlh_disc = omset_jual_produk

          # Update key items3
          data['omset_jual_produk'] = harga_stlh_disc
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
  
@app.get('/export_excel')
async def exportExcel(
  # tglAwal: str = Query(...),
  # tglAkhir: str = Query(...)
):
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

          q1 = """
            SELECT mt.id_transaksi,  mt.no_loker, mt.created_at AS tgl_beli, mt.jenis_transaksi, mt.jenis_tamu, mt.id_member, 
            k.nama_karyawan as nama_resepsionis,
            mt.total_harga, mt.disc, mt.grand_total, mt.metode_pembayaran
            FROM main_transaksi mt
            LEFT JOIN karyawan k ON mt.id_resepsionis = k.id_karyawan
          """
          await cursor.execute(q1)  
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
          corporate_ket = "LAPORAN PENJUALAN"
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
          column_main = [str(col) for col in main_data[0].keys()]
          ws.append(column_main)

          # Step 8 : Tambah data ke ws. jadikan list dlu, br ambil values
          for row in main_data:
            ws.append(list(row.values()))

          # Step 9 : Auto Adjust Column width berdasarkan konten
          for col in ws.columns:
            ws.column_dimensions[get_column_letter(col[0].column)].auto_size = True

          # Step 10 : Simpan Workbook Ke File
          file_path = "datapenjualan_platinum.xlsx"
          # Temporarily Make File Writable Before Overwriting
          if os.path.exists(file_path):
            os.chmod(file_path, 0o644)  # Grant write permissions (rw-r--r--)

          wb.save(file_path)
          os.chmod(file_path, 0o444)  # Set back to read-only

          # Step 11. Return Excelny sbg FileResponse
          return FileResponse(
            file_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename="datapenjualan_platinum.xlsx"
          )

        except aiomysqlerror as e:
          return JSONResponse({"Error": f"Sql Error {str(e)}"}, status_code=500)
        except HTTPException as e:
          return JSONResponse({"Error": f"HTTP Error {str(e.detail)}"}, status_code=e.status_code)
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)

