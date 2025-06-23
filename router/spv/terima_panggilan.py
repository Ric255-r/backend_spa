from typing import Optional
import json
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror
import datetime

app = APIRouter(prefix=("/spv"))

spv_connection = []

@app.websocket("/ws-spv")
async def spv_ws(
  websocket: WebSocket
):
  await websocket.accept()
  spv_connection.append(websocket)
  try:
    # Bikin Koneksi Ttp Nyala
    print("Hai Ws Nyala")
    await websocket.receive_text()

  except WebSocketDisconnect :
    spv_connection.remove(websocket)
    print("ws spv disonnect")

async def getlastestidpanggilan():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_panggilan FROM panggilan_kerja_sementara WHERE id_panggilan LIKE 'S%' ORDER BY id_panggilan DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_panggilan = items[0] if items is not None else None

        if id_panggilan is None:
          num = "1"
          strpad = "S" + num.zfill(2)
        else:
          getNum = id_panggilan[1:]
          num = int(getNum) + 1
          strpad = "S" + str(num).zfill(2)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  

@app.post('/daftarpanggilankerja')
async def daftarpanggilankerja(
    request: Request
  ):
    try:
      pool = await get_db()

      async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
          try:
            # 1. Start Transaction
            await conn.begin()
            lastidpanggilan = await getlastestidpanggilan()

            # 2. Execute querynya
            data = await request.json()
            q1 = "INSERT INTO panggilan_kerja_sementara(id_panggilan,ruangan,nama_terapis) VALUES(%s, %s, %s)"
            await cursor.execute(q1, (lastidpanggilan,data['ruangan'], data['nama_terapis']))

            # 3. Klo Sukses, dia bkl save ke db
            await conn.commit()

            q2 = "SELECT id_panggilan, ruangan, nama_terapis FROM panggilan_kerja_sementara"
            await cursor.execute(q2)
            all_records = await cursor.fetchall()
            message_data = [{
                  "id_panggilan": row[0],
                  "ruangan": row[1],
                  "nama_terapis": row[2],
                  "timestamp" : datetime.datetime.now().isoformat()
                } for row in all_records]
      
            for ws_con in spv_connection:
              await ws_con.send_text(
                json.dumps(message_data)
              )

            return "Succes"
          except aiomysqlerror as e:
            # Rollback Input Jika Error

            # Ambil Error code
            error_code = e.args[0] if e.args else "Unknown"
            
            await conn.rollback()
            return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
          
          except Exception as e:
            await conn.rollback()
            return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
          
    except Exception as e:
      return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)

@app.post('/daftarruangtunggu')
async def daftartunggu(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO ruang_tunggu(id_transaksi,id_terapis,nama_terapis,nama_ruangan) VALUES(%s, %s, %s, %s)"
          await cursor.execute(q1, (data['id_transaksi'], data['id_terapis'],data['nama_terapis'],data['nama_ruangan']))

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "Succes"
        except aiomysqlerror as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  

@app.get('/getdatapanggilankerja')
async def getdatapanggilankerja() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = "SELECT * FROM panggilan_kerja_sementara ORDER BY id_panggilan ASC"

        await cursor.execute(q1)  

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
@app.delete('/deletepanggilankerja')
async def deletepanggilankerja(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Execute querynya
          data = await request.json()
          q1 = "DELETE FROM panggilan_kerja_sementara WHERE id_panggilan = %s"
          await cursor.execute(q1, (data['id_panggilan']))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "succes"
        except aiomysqlerror.MySQLError as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error during insert : {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
