from typing import Optional

import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror

app = APIRouter(prefix=("/fasilitas"))

async def getlastestidfasilitas():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_fasilitas FROM paket_fasilitas WHERE id_fasilitas LIKE 'F%' ORDER BY id_fasilitas DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_fasilitas = items[0] if items is not None else None

        if id_fasilitas is None:
          num = "1"
          strpad = "F" + num.zfill(3)
        else:
          getNum = id_fasilitas[1:]
          num = int(getNum) + 1
          strpad = "F" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)

@app.post('/daftarfasilitas')
async def postfasilitas(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()
          lastidfasilitas = await getlastestidfasilitas()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO paket_fasilitas(id_fasilitas,nama_fasilitas,harga_fasilitas) VALUES(%s, %s, %s)"
          await cursor.execute(q1, (lastidfasilitas,data['nama_fasilitas'], data['harga_fasilitas']))

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

@app.get('/getnamafasilitas')
async def getnamafasilitas() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = "SELECT nama_fasilitas FROM paket_fasilitas ORDER BY id_fasilitas DESC"

        await cursor.execute(q1)

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)