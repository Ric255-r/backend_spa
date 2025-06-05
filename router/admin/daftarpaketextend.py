from typing import Optional

import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror

app = APIRouter(prefix=("/extend"))

async def getlatestidpaketextend():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_paket_extend FROM paket_extend WHERE id_paket_extend LIKE 'E%' ORDER BY id_paket_extend DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_category = items[0] if items is not None else None

        if id_category is None:
          num = "1"
          strpad = "E" + num.zfill(3)
        else:
          getNum = id_category[1:]
          num = int(getNum) + 1
          strpad = "E" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)

@app.post('/daftarpaketextend')
async def postpaketextend(
  request : Request
) :
  try:
    pool = await get_db()
    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()
          lastidpaketextend = await getlatestidpaketextend()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO paket_extend(id_paket_extend,nama_paket_extend,durasi_extend,harga_extend,komisi_terapis) VALUES(%s, %s, %s, %s, %s)"
          await cursor.execute(q1, (lastidpaketextend,data['nama_paket_extend'], data['durasi_extend'], data['harga_extend'], data['komisi_terapis']))

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "Success"
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

@app.get('/getnamapaketextend')
async def getnamapaketextend() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = "SELECT nama_paket_extend FROM paket_extend ORDER BY id_paket_extend DESC"

        await cursor.execute(q1)

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)