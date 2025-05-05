import asyncio
import json
from typing import Optional
import uuid
from fastapi import APIRouter, Query, Depends, File, Form, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
import pandas as pd
from aiomysql import Error as aiomysqlerror
from jwt_auth import access_security, refresh_security, verify_jwt
import calendar
import time

# Untuk Routingnya jadi http://192.xx.xx.xx:5500/api/fnb/endpointfunction
app = APIRouter(
  prefix="/massages",
  # dependencies=[Depends(verify_jwt)]
)

@app.get('/paket')
async def getPaket():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        # await asyncio.sleep(0.3)

        q1 = "SELECT * FROM paket_massage"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Paket Massage": str(e)}, status_code=500)
  

@app.get('/produk')
async def getPaket():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        q1 = "SELECT * FROM menu_produk"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Produk Massage": str(e)}, status_code=500)


@app.post('/store')
async def storeData(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Generate a new id_kategori *inside transaction safely*
          # q1 = """
          #   SELECT id_detail_transaksi FROM detail_transaksi WHERE id_detail_transaksi LIKE 'DT%' 
          #   ORDER BY id_detail_transaksi DESC LIMIT 1 FOR UPDATE
          # """
          # await cursor.execute(q1)
          # items = await cursor.fetchone()
          # id_dt = items[0] if items else None

          # if id_dt is None:
          #     num = 1  # First entry
          # else:
          #     getNum = id_dt[2:]  # Remove 'DT' and get number
          #     num = int(getNum) + 1

          # Karena tabel detail terpisah pisah, ga mungkin query diatas bs jalan. sehingga alternativeny get time now milisecond aj
          # Get current time in seconds since epoch (local time)
          seconds_local = time.time()
          # Convert to milliseconds
          milliseconds_local = int(seconds_local * 1000)
          # awalnya diambil dari variabel num
          new_id_dt = "DT" + str(milliseconds_local).zfill(16)

          # 3. Execute query 
          data = await request.json()
          # data main transaksi
          jenis_pembayaran = data['jenis_pembayaran']
          status_trans = data['status']

          # Pecah kedalam bentuk list, krna detail_trans bentuk array
          # Query Masukin Ke DetailTrans
          details = data.get('detail_trans', [])
          for item in details:
            if item['satuan'].lower() == "pcs":
              q2 = """
                INSERT INTO detail_transaksi_produk(
                  id_detail_transaksi, id_produk, qty, satuan, durasi_awal, 
                  total_durasi, harga_item, harga_total, status, is_addon
                ) 
                VALUES(
                  %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s
                )
              """
              await cursor.execute(q2, 
                (new_id_dt, item['id_paket_msg'], item['jlh'], item['satuan'], item['durasi_awal'],
                 item['jlh'] * item['durasi_awal'], item['harga_paket_msg'], item['harga_total'], status_trans, item['is_addon'])
              )
            else:
              q2 = """
                INSERT INTO detail_transaksi_paket(
                  id_detail_transaksi, id_paket, qty, satuan, durasi_awal, 
                  total_durasi, harga_item, harga_total, status, is_addon
                ) 
                VALUES(
                  %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s
                )
              """
              await cursor.execute(q2, (
                new_id_dt, item['id_paket_msg'], item['jlh'], item['satuan'], item['durasi_awal'],
                item['jlh'] * item['durasi_awal'], item['harga_paket_msg'], item['harga_total'], status_trans, item['is_addon']
              ))

          # false = awal
          if jenis_pembayaran == False:
            #Query Masukin ke Transaksi
            if data['metode_pembayaran'] == "qris" or data['metode_pembayaran'] == "debit":
              q3 = """
                UPDATE main_transaksi
                SET
                  id_loker = %s, jenis_transaksi = %s, id_detail_transaksi = %s, total_harga = %s, disc = %s, 
                  grand_total = %s, metode_pembayaran = %s, nama_akun = %s, no_rek = %s, 
                  nama_bank = %s, jumlah_bayar = %s, jumlah_kembalian = %s, jenis_pembayaran = %s, status = %s
                WHERE id_transaksi = %s
              """
              await cursor.execute(q3, (
                2, 'massage', new_id_dt, data['total_harga'], data['disc'], 
                data['grand_total'], data['metode_pembayaran'], data['nama_akun'], data['no_rek'],  
                data['nama_bank'], data['jumlah_bayar'], 0, jenis_pembayaran, status_trans,
                data['id_transaksi']  # <- moved to last parameter because it's in WHERE
              ))
            else:
              q3 = """
                UPDATE main_transaksi
                SET
                  id_loker = %s, jenis_transaksi = %s, id_detail_transaksi = %s, total_harga = %s, disc = %s, 
                  grand_total = %s, metode_pembayaran = %s, jumlah_bayar = %s, 
                  jumlah_kembalian = %s, jenis_pembayaran = %s, status = %s
                WHERE id_transaksi = %s
              """
              await cursor.execute(q3, (
                2, 'massage', new_id_dt, data['total_harga'], data['disc'], 
                data['grand_total'], data['metode_pembayaran'], data['jumlah_bayar'], 
                data['jumlah_bayar'] - data['grand_total'], jenis_pembayaran, status_trans,
                data['id_transaksi']  # <- moved to last parameter because it's in WHERE
              ))
          else:
            q3 = """
              UPDATE main_transaksi
              SET
                id_loker = %s, jenis_transaksi = %s, id_detail_transaksi = %s, total_harga = %s, disc = %s, 
                grand_total = %s, metode_pembayaran = %s, jumlah_bayar = %s, jumlah_kembalian = %s, 
                jenis_pembayaran = %s, status = %s
              WHERE id_transaksi = %s
            """
            await cursor.execute(q3, (
              2, 'massage', new_id_dt, data['total_harga'], data['disc'], 
              data['grand_total'], "-", 0, 0, jenis_pembayaran,  status_trans,
              data['id_transaksi']  # <- moved to last parameter because it's in WHERE
            ))


          # Masukin ke tabel kitchen juga
          # q4 = """
          #   INSERT INTO kitchen(
          #     id_transaksi, status_pesanan
          #   ) 
          #   VALUES(
          #     %s, %s
          #   )
          # """
          # await cursor.execute(q4, (data['id_transaksi'], 'pending'))
        
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          # Ini utk aktifkan websocket kirim ke admin
          # for ws_con in kitchen_connection:
          #   await ws_con.send_text(
          #     json.dumps({
          #       "id_transaksi": data['id_transaksi'],
          #       "status": "PENDING",
          #       "message": "Ada Order Baru"
          #     })
          #   )


          return JSONResponse(content={"status": "Success", "message": "Data Berhasil Diinput"}, status_code=200)
        except aiomysqlerror as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)
