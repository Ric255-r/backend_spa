from typing import Optional
import uuid
import aiomysql
from fastapi import APIRouter, Depends, File, Form, Query, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
import pandas as pd
import socket
from aiomysql import Error as aiomysqlerror

app = APIRouter(
  prefix="/listtrans",
)

@app.get('/cek_rating')
async def cek_rating(
  id_transaksi: str
) :
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      # wajib tambahi parameter aiomysql.DictCursor untuk buat hasil dalam bentuk dictionary
      # karena ak filter langsung make for loop yang item['is_addon']
      # jadi ga usah pake pd.Dataframe lagi
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try: 
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

          q1 = """
            SELECT * FROM rating WHERE id_transaksi = %s
          """ 
          await cursor.execute(q1, (id_transaksi, ))
          items = await cursor.fetchone()
          
          # Jika None di db, maka boleh isi rating, klo ad g blh
          return {
            "is_first_time": items is None,
            "data": items if items else {}
          }

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse({"Error aiomysql store rating": str(e)}, status_code=500)
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse({"Error HTTP": str(e.headers)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error store rating Trans": str(e)}, status_code=500)

@app.post('/store_rating')
async def store_rating(
  request: Request
) :
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      # wajib tambahi parameter aiomysql.DictCursor untuk buat hasil dalam bentuk dictionary
      # karena ak filter langsung make for loop yang item['is_addon']
      # jadi ga usah pake pd.Dataframe lagi
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try: 
          data = await request.json()

          await conn.begin()

          q1 = """
            INSERT INTO rating(id_transaksi, pelayanan_terapis, fasilitas, pelayanan_keseluruhan)          
            VALUES(%s, %s, %s, %s)
          """ 
          await cursor.execute(q1, (data['id_transaksi'], data['pelayanan_terapis'], data['fasilitas'], data['pelayanan_keseluruhan']))
          await conn.commit()


        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse({"Error aiomysql store rating": str(e)}, status_code=500)
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse({"Error HTTP": str(e.headers)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error store rating Trans": str(e)}, status_code=500)



# Buat Cek di struk
@app.get("/cek_struk_member")
async def check_struk(id_trans: str):
  try:
    pool = await get_db()
    async with pool.acquire() as conn:
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        
        # Query ini cek apakah dia pertamakali beli atau bkn
        # Member = pertamakali beli
        await cursor.execute("""
          SELECT * FROM main_transaksi WHERE jenis_transaksi = 'member' and id_transaksi = %s
        """, (id_trans, ))
        result = await cursor.fetchone()

        q1 = """
          SELECT * FROM main_transaksi WHERE id_transaksi = %s
        """
        await cursor.execute(q1, (id_trans, ))
        result1 = await cursor.fetchone()

        q2 = """
          SELECT dtm.*, p.nama_promo, m.nama as nama_member, m.no_hp 
          FROM detail_transaksi_member dtm
          INNER JOIN member m ON dtm.id_member = m.id_member
          INNER JOIN promo p ON dtm.kode_promo = p.kode_promo
          WHERE dtm.id_member = %s
        """
        await cursor.execute(q2, (result1['id_member'], ))
        result2 = await cursor.fetchall()

        return {
          "first_time_buy": result is not None, 
          "detail_member": result2 if result2 else []
        }
      
  except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
  
@app.post("/print")
async def print_pos_data(request: Request):
  raw_data = await request.body()
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as printer:
      printer.connect(('192.168.1.77', 9100))
      printer.sendall(raw_data)
    return {"status": "Printed successfully"}
  except Exception as e:
    return {"error": str(e)}
  
@app.get('/datatrans')
async def getDataTrans(
  hak_akses: Optional[str] = Query(None),
  start_date: Optional[str] = Query(None),
  end_date: Optional[str] = Query(None),
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        kondisi_q1 = ["mt.status != 'draft'"]
        params_q1 = []

        kondisi_q2 = []
        params_q2 = []

        # Bikin kondisi_q1 dan q2 Dinamis antara Resepsionis dan Owner
        if hak_akses == "resepsionis":
          kondisi_q1.append("DATE(mt.created_at) = CURDATE()")
          kondisi_q2.append("DATE(waktu_bayar) = CURDATE()")

        elif hak_akses == "owner" or hak_akses == "admin":
          if start_date and end_date:
            # Kondisi
            kondisi_q1.append("DATE(mt.created_at) BETWEEN %s and %s")
            kondisi_q2.append("DATE(waktu_bayar) BETWEEN %s and %s")
            # Parameternya
            params_q1.extend([start_date, end_date]) # extend() is for adding multiple elements from an iterable
            params_q2.extend([start_date, end_date])
          elif start_date:
            kondisi_q1.append("DATE(mt.created_at) = %s")
            kondisi_q2.append("DATE(waktu_bayar) = %s")
            params_q1.append(start_date)
            params_q2.append(start_date)
          else:
            kondisi_q1.append("DATE(mt.created_at) = CURDATE()")
            kondisi_q2.append("DATE(waktu_bayar) = CURDATE()")

        where_q1 = " AND ".join(kondisi_q1)
        where_q2 = " AND ".join(kondisi_q2)

        q1 = f"""
          SELECT mt.*, COALESCE(r.nama_ruangan, '-') AS nama_ruangan FROM main_transaksi mt 
          LEFT JOIN ruangan r ON mt.id_ruangan =  r.id_ruangan WHERE {where_q1}
          ORDER BY mt.id_transaksi ASC
        """
        print("Isi Q1 adalah ", q1)
        await cursor.execute(q1, params_q1)
        items = await cursor.fetchall()

        q2 = f"""
          SELECT * FROM pembayaran_transaksi WHERE {where_q2}
          ORDER BY id_transaksi ASC
        """
        await cursor.execute(q2, params_q2)
        items2 = await cursor.fetchall()
        data_cash = [item for item in items2 if item['metode_pembayaran'] == 'cash' and item['is_cancel'] == 0]
        data_debit = [item for item in items2 if item['metode_pembayaran'] == 'debit' and item['is_cancel'] == 0]
        data_kredit = [item for item in items2 if item['metode_pembayaran'] == 'kredit' and item['is_cancel'] == 0]
        data_qris = [item for item in items2 if item['metode_pembayaran'] == 'qris' and item['is_cancel'] == 0]
        
        omset_cash = 0
        for data in data_cash:
          omset_cash += data['jumlah_bayar']
        
        omset_debit = 0
        for data in data_debit:
          omset_debit += data['jumlah_bayar']
  
        omset_kredit = 0
        for data in data_kredit:
          omset_kredit += data['jumlah_bayar']
        
        omset_qris = 0
        for data in data_qris:
          omset_qris += data['jumlah_bayar']

        q3 = "SELECT NOW() AS tgl"
        await cursor.execute(q3)
        dataTgl = await cursor.fetchone()

        # # Ambil data detail transaksi dari record main
        # detail_ids = []
        # for record in records:
        #   detail_ids.append(record['id_transaksi'])
                   

        # # Buat Placeholder utk In Clause
        # placeholders = ",".join(['%s'] * len(detail_ids))

        # # Query product details
        # q_products = f"""
        #   SELECT dtp.*, m.nama_produk
        #   FROM detail_transaksi_produk dtp
        #   LEFT JOIN menu_produk m ON dtp.id_produk = m.id_produk
        #   WHERE dtp.id_transaksi IN ({placeholders})
        #   ORDER BY dtp.id_transaksi
        # """
        # await cursor.execute(q_products, detail_ids)
        # product_items = await cursor.fetchall()
        # product_columns = [kol[0] for kol in cursor.description]
        # df_products = pd.DataFrame(product_items, columns=product_columns)
        # product_records = df_products.to_dict('records')

        # # Query package details
        # q_paket = f"""
        #   SELECT dtp.*, m.nama_paket_msg
        #   FROM detail_transaksi_paket dtp
        #   LEFT JOIN paket_massage m ON dtp.id_paket = m.id_paket_msg
        #   WHERE dtp.id_transaksi IN ({placeholders})
        #   ORDER BY dtp.id_transaksi
        # """
        # await cursor.execute(q_paket, detail_ids)
        # paket_item = await cursor.fetchall()
        # paket_column = [kol[0] for kol in cursor.description]
        # df_paket = pd.DataFrame(paket_item, columns=paket_column)
        # paket_record = df_paket.to_dict('records')

        # # Query food details
        # q_food = f"""
        #   SELECT dtf.*, m.nama_fnb, k.nama_kategori AS kategori
        #   FROM detail_transaksi_fnb dtf
        #   LEFT JOIN menu_fnb m ON dtf.id_fnb = m.id_fnb
        #   LEFT JOIN kategori_fnb k ON m.id_kategori = k.id_kategori
        #   WHERE dtf.id_transaksi IN ({placeholders})
        #   ORDER BY dtf.id_transaksi
        # """
        # await cursor.execute(q_food, detail_ids)
        # food_item = await cursor.fetchall()
        # food_column = [kol[0] for kol in cursor.description]
        # df_food = pd.DataFrame(food_item, columns=food_column)
        # food_record = df_food.to_dict('records')

        # # Group detail records by detail_transaksi ID
        # from collections import defaultdict
        # products_by_detail = defaultdict(list)
        # for product in product_records:
        #   products_by_detail[product['id_transaksi']].append(product)

        # packages_by_detail = defaultdict(list)
        # for package in paket_record:
        #   packages_by_detail[package['id_transaksi']].append(package)

        # food_by_detail = defaultdict(list)
        # for item in food_record:
        #   food_by_detail[item['id_transaksi']].append(item)
        # # End Grouping

        # # Combine main records with their details
        # for record in records:
        #   detail_id = record['id_transaksi']
        #   record['isi_detail_produk'] = products_by_detail.get(detail_id, [])
        #   record['isi_detail_paket'] = packages_by_detail.get(detail_id, [])
        #   record['isi_detail_fnb'] = food_by_detail.get(detail_id, [])

        # return records
      
      return {
        "main_data": items,
        "data_cash": data_cash,
        "data_debit": data_debit,
        "data_kredit": data_kredit,
        "data_qris": data_qris,
        "total_cash": omset_cash,
        "total_debit": omset_debit,
        "total_kredit": omset_kredit,
        "total_qris": omset_qris,
        "tgl": dataTgl['tgl']
      }

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)
  
@app.get('/data_terapis/{id_trans}')
async def get_data_terapis(
  id_trans: str
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      # wajib tambahi parameter aiomysql.DictCursor untuk buat hasil dalam bentuk dictionary
      # karena ak filter langsung make for loop yang item['is_addon']
      # jadi ga usah pake pd.Dataframe lagi
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try: 
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

          q1 = """
            SELECT 
              tk.id,
              tk.id_transaksi,
              tk.id_terapis,
              TIME_FORMAT(tk.jam_datang, '%%H:%%i:%%s') as jam_datang,
              TIME_FORMAT(tk.jam_mulai, '%%H:%%i:%%s') as jam_mulai,
              TIME_FORMAT(tk.jam_selesai, '%%H:%%i:%%s') as jam_selesai,
              tk.alasan,
              tk.created_at,
              tk.is_tunda,
              tk.is_cancel,
              k.nama_karyawan 
            FROM terapis_kerja tk
            INNER JOIN karyawan k ON tk.id_terapis = k.id_karyawan
            WHERE tk.id_transaksi = %s
            ORDER BY tk.created_at DESC
          """
          await cursor.execute(q1, (id_trans, ))
          items = await cursor.fetchone()

          return items
        except aiomysqlerror as e:
          return JSONResponse({"Error aiomysql data terapis": str(e)}, status_code=500)
        except HTTPException as e:
          return JSONResponse({"Error HTTP": str(e.headers)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Data terapis Trans": str(e)}, status_code=500)
  

@app.get('/detailtrans/{id_trans}')
async def get_detail(
  id_trans: str
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      # wajib tambahi parameter aiomysql.DictCursor untuk buat hasil dalam bentuk dictionary
      # karena ak filter langsung make for loop yang item['is_addon']
      # jadi ga usah pake pd.Dataframe lagi
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try: 
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

          # Query product details
          q_products = f"""
            SELECT dtp.*, m.nama_produk
            FROM detail_transaksi_produk dtp
            LEFT JOIN menu_produk m ON dtp.id_produk = m.id_produk
            WHERE dtp.id_transaksi = %s
            ORDER BY dtp.id_transaksi
          """
          await cursor.execute(q_products, (id_trans, ))
          product_items = await cursor.fetchall()

          # Query package details
          q_paket = f"""
            SELECT dtp.*, 
              CASE 
                WHEN m.id_paket_msg IS NOT NULL THEN m.nama_paket_msg
                WHEN pe.id_paket_extend IS NOT NULL THEN pe.nama_paket_extend
                ELSE 'Unknown Paket'
              END AS nama_paket_msg
            FROM detail_transaksi_paket dtp
            LEFT JOIN paket_massage m ON dtp.id_paket = m.id_paket_msg
            LEFT JOIN paket_extend pe ON dtp.id_paket = pe.id_paket_extend
            WHERE dtp.id_transaksi = %s
            ORDER BY dtp.id_transaksi
          """
          await cursor.execute(q_paket, (id_trans, ))
          paket_item = await cursor.fetchall()
          
          # Query food details
          q_food = f"""
            SELECT dtf.*, m.nama_fnb, k.nama_kategori AS kategori
            FROM detail_transaksi_fnb dtf
            LEFT JOIN menu_fnb m ON dtf.id_fnb = m.id_fnb
            LEFT JOIN kategori_fnb k ON m.id_kategori = k.id_kategori
            WHERE dtf.id_transaksi = %s
            ORDER BY dtf.id_transaksi
          """
          await cursor.execute(q_food, (id_trans, ))
          food_item = await cursor.fetchall()

          q_fasilitas = """
            SELECT dtf.*, p.nama_fasilitas, p.harga_fasilitas
            FROM detail_transaksi_fasilitas dtf
            LEFT JOIN paket_fasilitas p ON dtf.id_fasilitas = p.id_fasilitas
            WHERE dtf.id_transaksi = %s
            ORDER BY dtf.id_transaksi
          """
          await cursor.execute(q_fasilitas, (id_trans, ))
          fasilitas_item = await cursor.fetchall()

          q_member = """
            SELECT dtm.*, p.nama_promo, m.nama, m.status as status_member, 
            m.no_hp
            FROM detail_transaksi_member dtm
            LEFT JOIN promo p ON dtm.kode_promo = p.kode_promo
            LEFT JOIN member m ON dtm.id_member = m.id_member
            WHERE dtm.id_transaksi = %s
            ORDER BY dtm.id_transaksi
          """
          await cursor.execute(q_member, (id_trans, ))
          member_item = await cursor.fetchall()
          print("member_item results:", member_item)

          q_harga_room = "SELECT harga_vip FROM main_transaksi WHERE id_transaksi = %s"
          await cursor.execute(q_harga_room, (id_trans, ))
          harga_room = await cursor.fetchall()

          # proses field product
          product_ori = [item for item in product_items if item['is_addon'] == 0]
          product_addon = []
          for item in product_items:
            if item['is_addon'] == 1:
              item['type'] = "product"
              product_addon.append(item)

          # Proses field Paket
          paket_ori =[item for item in paket_item if item['is_addon'] == 0]
          paket_addon = []
          for item in paket_item:
            if item['is_addon'] == 1:
              item['type'] = "paket"
              paket_addon.append(item)

          # Proses field food
          food_ori = [item for item in food_item if item['is_addon'] == 0]
          food_addon = []
          for item in food_item:
            if item['is_addon'] == 1:
              item['type'] = "fnb"
              food_addon.append(item)

          # proses field fasilitas
          fasilitas_ori = [item for item in fasilitas_item]

          #proses field member
          member_ori = [item for item in member_item]

          return {
            "detail_produk": product_ori,
            "detail_paket": paket_ori,
            "detail_food": food_ori,
            "detail_fasilitas": fasilitas_ori,
            "detail_member": member_ori,
            # satuin semua listnya
            "all_addon": product_addon + paket_addon + food_addon,
            "harga_ruangan": harga_room
          }
        except aiomysqlerror as e:
          return JSONResponse({"Error aiomysql Detail": str(e)}, status_code=500)
        except HTTPException as e:
          return JSONResponse({"Error HTTP": str(e.headers)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Data Detail Trans": str(e)}, status_code=500)
  
@app.put('/cancel_transaksi')
async def cancel_transaksi(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try: 
          await conn.begin()

          data = await request.json()

          qCheck = "SELECT 1 FROM users WHERE passwd = %s and hak_akses = %s"
          await cursor.execute(qCheck, (data['passwd'], '5')) #Spv = 5
          isExists = await cursor.fetchone()

          q_main = "SELECT * FROM main_transaksi WHERE id_transaksi = %s FOR UPDATE"
          await cursor.execute(q_main, (data['id_trans'], ))
          item_main = await cursor.fetchone()

          if isExists:
            q1 = """
              UPDATE main_transaksi SET is_cancel = %s WHERE id_transaksi = %s
            """
            await cursor.execute(q1, ('1', data['id_trans']))

            q2 = """
              UPDATE pembayaran_transaksi SET is_cancel = %s WHERE id_transaksi = %s
            """
            await cursor.execute(q2, ('1', data['id_trans']))

            q_details = [
              "UPDATE detail_transaksi_fasilitas SET status = %s WHERE id_transaksi = %s",
              "UPDATE detail_transaksi_fnb SET status = %s WHERE id_transaksi = %s",
              "UPDATE detail_transaksi_member SET status = %s WHERE id_transaksi = %s",
              "UPDATE detail_transaksi_paket SET status = %s WHERE id_transaksi = %s",
              "UPDATE detail_transaksi_produk SET status = %s WHERE id_transaksi = %s",
            ]
            for query in q_details:
              await cursor.execute(query, ('cancelled', data['id_trans']))

            q3 = """
              UPDATE ruangan SET status = %s WHERE id_ruangan = %s
            """
            await cursor.execute(q3, ('aktif', item_main['id_ruangan']))

            q4 = """
              UPDATE karyawan SET is_occupied = 0 WHERE id_karyawan = %s
            """
            await cursor.execute(q4, (item_main['id_terapis'], ))

            q5 = """
              UPDATE data_loker SET status = 0 WHERE nomor_locker = %s
            """
            await cursor.execute(q5, (item_main['no_loker'], ))

            q6 = """
              DELETE FROM durasi_kerja_sementara WHERE id_transaksi = %s
            """
            await cursor.execute(q6, (data['id_trans'], ))
              
            await conn.commit()

            return JSONResponse(content={"Success": "Berhasil Cancel Transaksi"}, status_code=200)
          else:
            return JSONResponse(content={"Gagal": "Tidak Ada Akses"}, status_code=401)

        except aiomysqlerror as e:  # Fixed typo from aiomysqlerror
            await conn.rollback()
            return JSONResponse(
                content={"success": False, "error": f"Database error: {str(e)}"},
                status_code=500
            )
        except HTTPException as e:
            await conn.rollback()
            return JSONResponse(
                content={"success": False, "error": str(e.detail)},
                status_code=e.status_code
          )

  except Exception as e:
    return JSONResponse(
      content={"success": False, "error": f"Unexpected error: {str(e)}"},
      status_code=500
    )
  
@app.put('/update_fnb')
async def update_idtrans_fnb(
  request: Request
) :
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try: 
          await conn.begin()

          data = await request.json()
          current_id = data['current_id_trans']
          new_id = data['new_id_trans']

          q1 = """
            UPDATE main_transaksi SET nama_tamu = %s WHERE id_transaksi = %s
          """
          await cursor.execute(q1, (new_id, current_id))
          await conn.commit()
          
        except aiomysqlerror as e:  # Fixed typo from aiomysqlerror
            await conn.rollback()
            return JSONResponse(
                content={"success": False, "error": f"Database error: {str(e)}"},
                status_code=500
            )
        except HTTPException as e:
            await conn.rollback()
            return JSONResponse(
                content={"success": False, "error": str(e.detail)},
                status_code=e.status_code
          )

  except Exception as e:
    return JSONResponse(
      content={"success": False, "error": f"Unexpected error: {str(e)}"},
      status_code=500
    )
  



# @app.get('/detailtrans')
# async def getDataDetailTrans():
#   try:
#     pool = await get_db() # Get The pool

#     async with pool.acquire() as conn:  # Auto Release
#       async with conn.cursor() as cursor:
#         await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
#         q1 = """
#              SELECT 
#               mt.id_transaksi,
#               mt.id_detail_transaksi,

#               GROUP_CONCAT(DISTINCT dtp.id_produk) AS produk_list,

#               GROUP_CONCAT(DISTINCT dt.id_fnb) AS fnb_list,

#               GROUP_CONCAT(DISTINCT dtpk.id_paket) AS paket_list,

#               GROUP_CONCAT(DISTINCT COALESCE(dtp.id_produk, '')) AS produk_list_detail,
#               GROUP_CONCAT(DISTINCT COALESCE(dtp.qty, 0)) AS produk_qty_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtp.satuan, '')) AS produk_satuan_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtp.harga_item, 0)) AS produk_harga_item_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtp.harga_total, 0)) AS produk_harga_total_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtp.durasi_awal, 0)) AS produk_durasi_awal_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtp.total_durasi, 0)) AS produk_total_durasi_list,

#               GROUP_CONCAT(DISTINCT COALESCE(dtpk.id_paket, '')) AS paket_list_detail,
#               GROUP_CONCAT(DISTINCT COALESCE(dtpk.qty, 0)) AS paket_qty_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtpk.satuan, '')) AS paket_satuan_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtpk.durasi_awal, 0)) AS paket_durasi_awal_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtpk.total_durasi, 0)) AS paket_total_durasi_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtpk.harga_item, 0)) AS paket_harga_item_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dtpk.harga_total, 0)) AS paket_harga_total_list,

#               GROUP_CONCAT(DISTINCT COALESCE(dt.qty, 0)) AS fnb_qty_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dt.satuan, '')) AS fnb_satuan_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dt.harga_item, 0)) AS fnb_harga_item_list,
#               GROUP_CONCAT(DISTINCT COALESCE(dt.harga_total, 0)) AS fnb_harga_total_list

#             FROM main_transaksi mt
#             LEFT JOIN detail_transaksi dt ON mt.id_detail_transaksi = dt.id_detail_transaksi
#             LEFT JOIN detail_transaksi_produk dtp ON mt.id_detail_transaksi = dtp.id_detail_transaksi
#             LEFT JOIN detail_transaksi_paket dtpk ON mt.id_detail_transaksi = dtpk.id_detail_transaksi
#             GROUP BY mt.id_transaksi, mt.id_detail_transaksi;
#               """
#         await cursor.execute("SET SESSION group_concat_max_len = 100000;")
#         await cursor.execute(q1)
        

#         items = await cursor.fetchall()

#         column_name = []
#         for kol in cursor.description:
#           column_name.append(kol[0])

#         df = pd.DataFrame(items, columns=column_name)
#         return df.to_dict('records')

#   except Exception as e:
#     return JSONResponse({"Error Get Data Detail Trans": str(e)}, status_code=500)





# @app.get('/detailtrans')
# async def getDataDetailTrans():
#   try:
#     pool = await get_db() # Get The pool

#     async with pool.acquire() as conn:  # Auto Release
#       async with conn.cursor() as cursor:
#         await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
#         q1 = "SELECT dt.*, mt.* FROM detail_transaksi dt LEFT JOIN main_transaksi mt ON dt.id_detail_transaksi = mt.id_detail_transaksi ORDER BY dt.id_detail_transaksi ASC"
#         await cursor.execute(q1)
#         q2 = "SELECT dt.*, mt.* FROM detail_transaksi_paket dt LEFT JOIN main_transaksi mt ON dt.id_detail_transaksi = mt.id_detail_transaksi ORDER BY dt.id_detail_transaksi ASC"
#         await cursor.execute(q2)
#         q3 = "SELECT dt.*, mt.* FROM detail_transaksi_produk dt LEFT JOIN main_transaksi mt ON dt.id_detail_transaksi = mt.id_detail_transaksi ORDER BY dt.id_detail_transaksi ASC"
#         await cursor.execute(q3)

#         items = await cursor.fetchall()

#         column_name = []
#         for kol in cursor.description:
#           column_name.append(kol[0])

#         df = pd.DataFrame(items, columns=column_name)
#         return df.to_dict('records')

#   except Exception as e:
#     return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)