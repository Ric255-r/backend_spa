import json
import time
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Query, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
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

# Untuk Routingnya jadi http://192.xx.xx.xx:5500/api/fnb/endpointfunction
app = APIRouter(
  prefix="/fnb",
  # dependencies=[Depends(verify_jwt)]
)


# Penggantinya Create Draft Transaksi
# @app.get('/lastId')
# async def getLatestTransaksi():
#   try:
#     pool = await get_db() # Get The pool

#     async with pool.acquire() as conn:  # Auto Release
#       async with conn.cursor() as cursor:

#         q1 = """
#           SELECT id_transaksi FROM main_transaksi 
#           WHERE id_transaksi LIKE 'TF%' 
#           ORDER BY CAST(SUBSTRING(id_transaksi, 3) AS UNSIGNED) DESC
#           LIMIT 1
#           FOR UPDATE
#         """
#         await cursor.execute(q1)

#         items = await cursor.fetchone() #id transaksi terletak di index ke-0
#         id_trans = items[0] if items is not None else None

#         if id_trans is None:
#           num = "1"
#           strpad = "TF" + num.zfill(4)
#         else:
#           getNum = id_trans[2:]
#           num = int(getNum) + 1
#           strpad = "TF" + str(num).zfill(4)

#         return strpad


#   except Exception as e:
#     return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)

kitchen_connection = []

@app.websocket("/ws-kitchen")
async def kitchen_ws(
  websocket: WebSocket
):
  await websocket.accept()
  kitchen_connection.append(websocket)
  try:
    # Bikin Koneksi Ttp Nyala
    print("Hai Ws Nyala")
    await websocket.receive_text()

  except WebSocketDisconnect :
    kitchen_connection.remove(websocket)
  


@app.get('/menu')
async def getMenu():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        q1 = "SELECT * FROM menu_fnb"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  
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

          # 3. Execute query DT
          data = await request.json()

          # Pecah kedalam bentuk list, krna detail_trans bentuk array
          # Query Masukin Ke DetailTrans
          details = data.get('detail_trans', [])
          for item in details:
            # Samain dengan kode detailtransaksi massage
            # seconds_local = time.time()
            # # Convert to milliseconds
            # milliseconds_local = int(seconds_local * 1000)
            # # awalnya diambil dari variabel num
            # new_id_dt = "DT" + str(milliseconds_local).zfill(16)
            new_id_dt = f"DT{uuid.uuid4().hex[:16]}"

            q2 = """
              INSERT INTO detail_transaksi_fnb(
                id_detail_transaksi, id_transaksi, id_fnb, qty, satuan, harga_item, harga_total
              ) 
              VALUES(
                %s, %s, %s, %s, %s, %s, %s
              )
            """
            await cursor.execute(q2, (new_id_dt, data['id_transaksi'], item['id_fnb'], item['jlh'], item['satuan'], item['harga_fnb'], item['harga_total']))

            # Masukin ke tabel kitchen juga
            q4 = """
              INSERT INTO kitchen(
                id_transaksi, id_detail_transaksi, status_pesanan, is_addon
              ) 
              VALUES(
                %s, %s, %s, %s
              )
            """
            await cursor.execute(q4, (data['id_transaksi'], new_id_dt, 'pending', 0))

          #Query Masukin ke Transaksi
          if data['metode_pembayaran'] == "qris" or data['metode_pembayaran'] == "debit":
            q3 = """
              UPDATE main_transaksi
              SET
                no_loker = %s, jenis_transaksi = %s, total_harga = %s, disc = %s, 
                grand_total = %s, metode_pembayaran = %s, nama_akun = %s, no_rek = %s, 
                nama_bank = %s, jumlah_bayar = %s, jumlah_kembalian = %s, status = %s
              WHERE id_transaksi = %s
            """
            await cursor.execute(q3, (
              -1, 'fnb', data['total_harga'], data['disc'], 
              data['grand_total'], data['metode_pembayaran'], data['nama_akun'], data['no_rek'],  
              data['nama_bank'], data['jumlah_bayar'], 0, 'paid',
              data['id_transaksi']  # <- moved to last parameter because it's in WHERE
            ))
          else:

            q3 = """
              UPDATE main_transaksi
              SET
                no_loker = %s, jenis_transaksi = %s, total_harga = %s, disc = %s, 
                grand_total = %s, metode_pembayaran = %s, jumlah_bayar = %s, 
                jumlah_kembalian = %s, status = %s
              WHERE id_transaksi = %s
            """
            await cursor.execute(q3, (
              -1, 'fnb', data['total_harga'], data['disc'], 
              data['grand_total'], data['metode_pembayaran'], data['jumlah_bayar'], 
              data['jumlah_bayar'] - data['grand_total'], 'paid',
              data['id_transaksi']  # <- moved to last parameter because it's in WHERE
            ))

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          # Ini utk aktifkan websocket kirim ke admin
          for ws_con in kitchen_connection:
            await ws_con.send_text(
              json.dumps({
                "id_transaksi": data['id_transaksi'],
                "status": "PENDING",
                "message": "Ada Order Baru"
              })
            )


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
  

@app.get('/selected_food')
async def getFood(
  id_trans: str = Query()
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # Paksa Buat Cursor Baru
          await cursor.close()
          cursor = await conn.cursor()
          # End Paksa

          # Query Paket
          q_paket = f"""
            SELECT dtf.*, m.nama_fnb FROM detail_transaksi_fnb dtf 
            INNER JOIN menu_fnb m ON dtf.id_fnb = m.id_fnb
            WHERE dtf.id_transaksi = %s
          """ 
          await cursor.execute(q_paket, (id_trans, ))

          column_names = []
          for kol in cursor.description:
            column_names.append(kol[0])

          items = await cursor.fetchall()

          # kalo items hanya return single row, lapis make [] krn pake fetchone, klo fetchall g ush lapis.
          df = pd.DataFrame(items, columns=column_names)

          # utk return data. ambil index ke-0 krn dia return dalam bentuk list/array
          return df.to_dict('records')

        except HTTPException as e:
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
        finally:
          if cursor:
            await cursor.close()
        

  except Exception as e:
    return JSONResponse(content={"status":"error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
@app.post('/store_addon')
async def storeAddOn(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 3. Execute query DT
          data = await request.json()
          id_trans = data['id_transaksi']

          # Pecah kedalam bentuk list, krna detail_trans bentuk array
          # Query Masukin Ke DetailTrans
          details = data.get('detail_trans', [])
          for item in details:
            new_id_dt = f"DT{uuid.uuid4().hex[:16]}"
            q2 = """
              INSERT INTO detail_transaksi_fnb(
                id_detail_transaksi, id_transaksi, id_fnb, qty, satuan, harga_item, harga_total, status, is_addon
              ) 
              VALUES(
                %s, %s, %s, %s, %s, %s, %s, %s, %s
              )
            """
            await cursor.execute(q2, (new_id_dt, id_trans, item['id_fnb'], item['jlh'], item['satuan'], item['harga_fnb'], item['harga_total'], 'unpaid', 1))

            # Masukin ke tabel kitchen juga
            q4 = """
              INSERT INTO kitchen(
                id_transaksi, id_detail_transaksi, status_pesanan, is_addon
              ) 
              VALUES(
                %s, %s, %s, %s
              )
            """
            await cursor.execute(q4, (id_trans, new_id_dt, 'pending', 1))
        
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          # Ini utk aktifkan websocket kirim ke admin
          for ws_con in kitchen_connection:
            await ws_con.send_text(
              json.dumps({
                "id_transaksi": data['id_transaksi'],
                "status": "PENDING",
                "message": "Ada Order Baru"
              })
            )


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