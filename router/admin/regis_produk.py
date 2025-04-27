from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
import pandas as pd
from aiomysql import Error as aiomysqlerror

# Untuk Routingnya jadi http://192.xx.xx.xx:5500/api/produk/endpointfunction
app = APIRouter(
  prefix="/produk",
)

@app.get('/kategoriproduk')
async def getKategoriProduk():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        q1 = "SELECT id_kategori, nama_kategori FROM kategori_produk"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Kategori produk": str(e)}, status_code=500)
  
@app.post('/post_produk')
async def postProduk(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          id_produk = await getLatestProduk()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO menu_produk(id_produk, id_kategori, nama_produk, harga_produk, stok) VALUES(%s, %s, %s, %s, %s)"
          await cursor.execute(q1, (id_produk, data['id_kategori'], data['nama_produk'], data['harga_produk'], data['stok']) )

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return JSONResponse(content={"status": "Success", "message": "Data Berhasil Diinput"}, status_code=200)
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

@app.post('/postkategori')
async def postKategori(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          id_kategori = await getLatestKategori()
          if not id_kategori:
              return JSONResponse(content={"status": "Error", "message": "Failed to generate id_kategori"}, status_code=500)

          # print(f"Received data: {data}")
          # print(f"Generated ID: {id_kategori}")

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO kategori_produk(id_kategori, nama_kategori) VALUES(%s, %s)"
          await cursor.execute(q1, (id_kategori, data['nama_kategori']) )
          print("Query executed successfully")

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()
          print("Database commit success")

          return JSONResponse(content={"status": "Success", "message": "Data Berhasil Diinput"}, status_code=200)
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

async def getLatestProduk():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_produk FROM menu_produk WHERE id_produk LIKE 'P%' ORDER BY id_produk DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_produk = items[0] if items is not None else None

        if id_produk is None:
          num = "1"
          strpad = "P" + num.zfill(3)
        else:
          getNum = id_produk[1:]
          num = int(getNum) + 1
          strpad = "P" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  
@app.get('/hai')
async def getLatestKategori():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_kategori FROM kategori_produk WHERE id_kategori LIKE 'K%' ORDER BY id_kategori DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_kategori = items[0] if items is not None else None

        if id_kategori is None:
          num = "1"
          strpad = "K" + num.zfill(3)
        else:
          getNum = id_kategori[1:]

          num = int(getNum) + 1
          strpad = "K" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)