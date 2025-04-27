from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror

app = APIRouter(prefix=("/fnb"))

@app.get('/getkategori')
async def getkategori(
  request:Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        q1 = "SELECT id_kategori, nama_kategori FROM kategori_fnb"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        kolom_menu = []
        for kolom in cursor.description:
          kolom_menu.append(kolom[0])
        print(kolom)
          
        df = pd.DataFrame(items,columns=kolom_menu)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)


async def getlatestidfood():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_fnb FROM menu_fnb WHERE id_fnb LIKE 'F%' ORDER BY id_fnb DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_menuu = items[0] if items is not None else None

        if id_menuu is None:
          num = "1"
          strpad = "F" + num.zfill(3)
        else:
          getNum = id_menuu[1:]
          num = int(getNum) + 1
          strpad = "F" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)


@app.post('/daftarpaket')
async def postpaket(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()
          lastidfnb = await getlatestidfood()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO menu_fnb(id_fnb,nama_fnb, harga_fnb,id_kategori,status_fnb) VALUES(%s, %s, %s, %s, %s)"
          await cursor.execute(q1, (lastidfnb,data['nama_fnb'], data['harga_fnb'], data['id_kategori'],data['status']))

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
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)

async def getlatestidkategori():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_kategori FROM kategori_fnb WHERE id_kategori LIKE 'M%' ORDER BY id_kategori DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_category = items[0] if items is not None else None

        if id_category is None:
          num = "1"
          strpad = "M" + num.zfill(3)
        else:
          getNum = id_category[1:]
          num = int(getNum) + 1
          strpad = "M" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)


@app.post('/daftarkategori')
async def postkategori(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()
          lastidkategori = await getlatestidkategori()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO kategori_fnb(id_kategori,nama_kategori) VALUES(%s, %s)"
          await cursor.execute(q1, (lastidkategori,data['nama_kategori']))

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
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)