from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Query, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
import pandas as pd
from aiomysql import Error as aiomysqlerror
from jwt_auth import access_security, refresh_security
from datetime import timedelta


app = APIRouter(
  prefix="/extend"
)

@app.get('/get_data/{id_trans}')
async def getdatalocker(
  id_trans: str
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = """
          SELECT dtp.*, pm.nama_paket_msg, pm.harga_paket_msg AS hrg_item FROM detail_transaksi_paket dtp 
          INNER JOIN paket_massage pm ON dtp.id_paket = pm.id_paket_msg
          WHERE dtp.id_transaksi = %s AND dtp.is_returned != 1
        """
        await cursor.execute(q1, (id_trans, ))  

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # Detail Transaksi Produk
        q2 = """
          SELECT dtp.*, mp.nama_produk, mp.harga_produk AS hrg_item FROM detail_transaksi_produk dtp 
          INNER JOIN menu_produk mp ON dtp.id_produk = mp.id_produk
          WHERE dtp.id_transaksi = %s
        """
        await cursor.execute(q2, (id_trans, ))  

        items2 = await cursor.fetchall()

        kolom_menu2 = [kolom[0] for kolom in cursor.description]
        df2 = pd.DataFrame(items2, columns=kolom_menu2)

        # print(" Final fetched items:", items)
        return {
          "paket": df.to_dict('records'),
          "produk": df2.to_dict('records')
        }
      
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
@app.post('/save_addon')
async def save_addon(
  request: Request
):
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()
          # id_dt = data['id_detail_transaksi']
          id_main = data['id_transaksi']
          detail_paket = data.get('detail_paket', [])
          detail_produk = data.get('detail_produk', [])
          durasi_tambahan = 0
          total_addon = 0

          for item in detail_paket:
            new_id_dt = f"DT{uuid.uuid4().hex[:16]}"
            durasi_tambahan += item['extended_duration']
            
            # qty = int(item['extended_duration']) / int(item['durasi_awal'])
            # harga_total = qty * item['harga_item']

            qty = item['qty']
            harga_total = item['harga_total']
            total_addon += harga_total

            q1 = """
              INSERT INTO detail_transaksi_paket(
                id_detail_transaksi, id_transaksi, id_paket, qty, satuan, 
                durasi_awal, total_durasi, harga_item, harga_total, 
                status, is_addon
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            await cursor.execute(q1, (
              new_id_dt, id_main, item['id_paket'], qty, item['satuan'], 
              item['durasi_awal'], item['extended_duration'], item['harga_item'], harga_total,
              'unpaid', 1
            ))  

          for item in detail_produk:
            new_id_dt = f"DT{uuid.uuid4().hex[:16]}"
            durasi_tambahan += item['extended_duration']

            # qty = int(item['extended_duration']) / int(item['durasi_awal'])
            # harga_total = qty * item['harga_item']
            # total_addon += harga_total
            qty = item['qty']
            harga_total = item['harga_total']
            total_addon += harga_total

            q2 = """
              INSERT INTO detail_transaksi_produk(
                id_detail_transaksi, id_transaksi, id_produk, qty, satuan, 
                durasi_awal, total_durasi, harga_item, harga_total, 
                status, is_addon
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            await cursor.execute(q2, (
              new_id_dt, id_main, item['id_produk'], qty, item['satuan'], 
              item['durasi_awal'], item['extended_duration'], item['harga_item'], harga_total,
              'unpaid', 1
            ))  

          # Select kode maintransaksi utk update addon
          q3 = """
            SELECT total_addon FROM main_transaksi WHERE id_transaksi = %s
          """
          await cursor.execute(q3, (id_main, ))  

          itemsTrans = await cursor.fetchone()
          addon_awal = itemsTrans[0]

          q4 = """
            UPDATE main_transaksi SET total_addon = %s WHERE id_transaksi = %s
          """
          await cursor.execute(q4, (total_addon + addon_awal, id_main))  
          await conn.commit()

          # Select durasi_kerja_sementara utk dapetin sum_durasi_menit yg tersimpan
          q5 = """
            SELECT sum_durasi_menit FROM durasi_kerja_sementara WHERE id_transaksi = %s
          """
          await cursor.execute(q5, (id_main, ))  

          itemsDurasi = await cursor.fetchone()
          savedDurasi = itemsDurasi[0]

          # Baru update, dgn kalkulasi menit yg lama dgn yg di extend
          q6 = """
            UPDATE durasi_kerja_sementara SET sum_durasi_menit = %s WHERE id_transaksi = %s
          """
          await cursor.execute(q6, (savedDurasi + durasi_tambahan, id_main))  
          await conn.commit()

        except aiomysqlerror as e:
          return JSONResponse(content={"Error": f"err mysql Save {e}"}, status_code=500)

        except HTTPException as e:
          return JSONResponse(content={"Error": f"http gagal Save {e}"}, status_code=e.status_code)
        
        return {
          "durasi_baru": savedDurasi + durasi_tambahan,
        }

  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  




