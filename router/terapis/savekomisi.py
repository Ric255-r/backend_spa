from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror
import asyncio

app = APIRouter(prefix=("/komisi"))

@app.get('/getkomisipaket')
async def getkomisipaket(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT tipe_komisi, nominal_komisi,harga_paket_msg FROM paket_massage WHERE nama_paket_msg = %s"
        await cursor.execute(q1,(data['nama_paket'],))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)

@app.post('/daftarkomisipekerja')
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

          # 2. Execute querynya
          data = await request.json()
          print(data)
          q1 = "INSERT INTO komisi(id_karyawan, id_transaksi, nominal_komisi) VALUES(%s, %s, %s)"
          await cursor.execute(q1, (data['id_karyawan'], data['id_transaksi'], data['nominal_komisi']))

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

@app.get('/getidpaket')
async def getidpaket(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT id_paket_msg FROM paket_massage WHERE nama_paket_msg = %s"
        await cursor.execute(q1,(data['nama_paket_msg']))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)

@app.get('/getidterapis')
async def getidpaket(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT id_karyawan FROM karyawan WHERE nama_karyawan = %s"
        await cursor.execute(q1,(data['nama_karyawan']))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)

@app.get('/getqtypaket')
async def getqtypaket(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT qty FROM detail_transaksi_paket WHERE id_transaksi = %s and id_paket = %s"
        await cursor.execute(q1,(data['id_transaksi'],data['id_paket']))

        items = await cursor.fetchall()

        qty_list = [int(item[0]) for item in items]

        return JSONResponse({"qty" : qty_list})

        # column_name = []
        # for kol in cursor.description:
        #   column_name.append(kol[0])

        # df = pd.DataFrame(items, columns=column_name)
        # return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)

@app.get('/getkomisiproduk')
async def getkomisiproduk(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT tipe_komisi, nominal_komisi, harga_produk FROM menu_produk WHERE nama_produk = %s"
        await cursor.execute(q1,(data['nama_produk'],))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)

@app.get('/getqtyproduk')
async def getqtyproduk(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT qty FROM detail_transaksi_produk WHERE id_transaksi = %s and id_produk = %s"
        await cursor.execute(q1,(data['id_transaksi'],data['id_produk']))

        items = await cursor.fetchall()

        qty_list = [int(item[0]) for item in items]

        return JSONResponse({"qty" : qty_list})

        # column_name = []
        # for kol in cursor.description:
        #   column_name.append(kol[0])

        # df = pd.DataFrame(items, columns=column_name)
        # return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)