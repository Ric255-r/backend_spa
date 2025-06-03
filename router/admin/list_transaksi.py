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
from aiomysql import Error as aiomysqlerror

app = APIRouter(
  prefix="/listtrans",
)

# Buat Cek di struk
@app.get("/cek_struk_member")
async def check_struk(id_trans: str):
  try:
    pool = await get_db()
    async with pool.acquire() as conn:
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        
        # Query ini cek apakah dia pertamakali beli atau bkn
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
  
@app.get('/datatrans')
async def getDataTrans(
  hak_akses: Optional[str] = Query(None)
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = f"""
          SELECT mt.*, COALESCE(r.nama_ruangan, '-') AS nama_ruangan FROM main_transaksi mt 
          LEFT JOIN ruangan r ON mt.id_ruangan = r.id_ruangan WHERE mt.status != 'draft'
          {'AND DATE(mt.created_at) = CURDATE()' if hak_akses == 'resepsionis' else ''}
          ORDER BY mt.id_transaksi ASC
        """
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df_main = pd.DataFrame(items, columns=column_name)
        records = df_main.to_dict('records')

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
      
      return records


  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)
  

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
            SELECT dtp.*, m.nama_paket_msg
            FROM detail_transaksi_paket dtp
            LEFT JOIN paket_massage m ON dtp.id_paket = m.id_paket_msg
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
            "all_addon": product_addon + paket_addon + food_addon 
          }
        except aiomysqlerror as e:
          return JSONResponse({"Error aiomysql Detail": str(e)}, status_code=500)
        except HTTPException as e:
          return JSONResponse({"Error HTTP": str(e.headers)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Data Detail Trans": str(e)}, status_code=500)



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