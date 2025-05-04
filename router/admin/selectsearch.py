from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror
import asyncio

app = APIRouter(prefix=("/search"))

@app.get('/searchdatamassage')
async def searchdatamassage(
  request: Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        data = await request.json()
        q1 = "SELECT * FROM paket_massage WHERE nama_paket_msg LIKE %s ORDER BY id_paket_msg ASC"
        search_term = f"%{data['nama_paket_msg']}%"
        await cursor.execute(q1, (search_term,))

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)

@app.get('/searchdatafnb')
async def searchdatafnb(
  request: Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        data = await request.json()
        q1 = "SELECT * FROM menu_fnb WHERE nama_fnb LIKE %s ORDER BY id_fnb ASC"
        search_term = f"%{data['nama_fnb']}%"
        await cursor.execute(q1, (search_term,))

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
@app.get('/searchdataproduk')
async def searchdataproduk(
  request: Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        data = await request.json()
        q1 = "SELECT * FROM menu_produk WHERE nama_produk LIKE %s ORDER BY id_produk ASC"
        search_term = f"%{data['nama_produk']}%"
        await cursor.execute(q1, (search_term,))

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
@app.get('/searchdatafasilitas')
async def searchdatafasilitas(
  request: Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        data = await request.json()
        q1 = "SELECT * FROM paket_fasilitas WHERE nama_fasilitas LIKE %s ORDER BY id_fasilitas ASC"
        search_term = f"%{data['nama_fasilitas']}%"
        await cursor.execute(q1, (search_term,))

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)