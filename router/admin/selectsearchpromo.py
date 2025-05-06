from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror
import asyncio

app = APIRouter(prefix=("/searchpromo"))

  
@app.get('/searchpromohappyhour')
async def searchpromohappyhour(
  request: Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()
        # await cursor.execute("COMMIT;")
        q1 = """
            SELECT a.kode_promo, a.nama_promo, 
            b.detail_kode_promo, b.senin, b.selasa, b.rabu, b.kamis, b.jumat, b.sabtu, b.minggu,
            TIME_FORMAT(b.jam_mulai, '%%H:%%i') AS jam_mulai, 
            TIME_FORMAT(b.jam_selesai, '%%H:%%i') AS jam_selesai, 
            b.disc, b.member, b.vip 
            FROM promo a 
            INNER JOIN detail_promo_happyhour b 
            ON a.kode_detail_promo = b.detail_kode_promo WHERE a.nama_promo LIKE %s
            ORDER BY a.kode_promo ASC;
            """
        search_term = f"%{data['nama_promo']}%"
        await cursor.execute(q1, (search_term,))

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)

@app.get('/searchpromokunjungan')
async def searchpromokunjungan(
  request: Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        data = await request.json()
        q1 = """
            SELECT a.kode_promo, a.nama_promo, 
            b.detail_kode_promo, b.limit_kunjungan, b.harga_promo
            FROM promo a 
            INNER JOIN detail_promo_kunjungan b 
            ON a.kode_detail_promo = b.detail_kode_promo WHERE a.nama_promo LIKE %s
            ORDER BY a.kode_promo ASC;
            """
        search_term = f"%{data['nama_promo']}%"
        await cursor.execute(q1, (search_term,))

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
@app.get('/searchpromotahunan')
async def searchpromotahunan(
  request: Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        data = await request.json()
        q1 = """
            SELECT a.kode_promo, a.nama_promo, 
            b.detail_kode_promo, b.jangka_tahun, b.harga_promo
            FROM promo a 
            INNER JOIN detail_promo_tahunan b 
            ON a.kode_detail_promo = b.detail_kode_promo  WHERE a.nama_promo LIKE %s
            ORDER BY a.kode_promo ASC;
            """
        search_term = f"%{data['nama_promo']}%"
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