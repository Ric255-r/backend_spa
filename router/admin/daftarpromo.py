from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror
import asyncio

app = APIRouter(prefix=("/promo"))


async def getlastestiddetailpromohappyhour():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        q1 = "SELECT detail_kode_promo FROM detail_promo_happyhour WHERE detail_kode_promo LIKE 'DP%' ORDER BY detail_kode_promo DESC"
        cc = await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_detail_kodepromo = items[0] if items is not None else None
        if id_detail_kodepromo is None:
          num = "1"
          strpad = "DP" + num.zfill(3)
        else:
          getNum = id_detail_kodepromo[2:]
          num = int(getNum) + 1
          strpad = "DP" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)

@app.get('/getlastestidpromo') 
async def getlastestidpromo():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        q1 = "SELECT kode_promo FROM promo WHERE kode_promo LIKE 'P%' ORDER BY kode_promo DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_kodepromo = items[0] if items is not None else None

        if id_kodepromo is None:
          num = "1"
          strpad = "P" + num.zfill(3)
        else:
          getNum = id_kodepromo[1:]
          num = int(getNum) + 1
          strpad = "P" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  

@app.post('/daftarpromohappyhour')
async def postpromohappyhour(
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
          lastidpromo = await getlastestidpromo()
          lastiddetailpromo = await getlastestiddetailpromohappyhour()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO promo(kode_promo,nama_promo,kode_detail_promo) VALUES(%s, %s, %s)"
          await cursor.execute(q1, (data['kode_promo'],data['nama_promo'],lastiddetailpromo))

          q2 = "INSERT INTO detail_promo_happyhour(detail_kode_promo,senin,selasa,rabu,kamis,jumat,sabtu,minggu,jam_mulai,jam_selesai,disc,member,vip) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
          await cursor.execute(q2, (lastiddetailpromo,data['senin'],data['selasa'],data['rabu'],data['kamis'],data['jumat'],data['sabtu'],data['minggu'],data['jam_mulai'],data['jam_selesai'],data['disc'],data['member'],data['vip']))
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

@app.get('/getidpromo')
async def getidpromo() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = "SELECT kode_promo,nama_promo FROM promo ORDER BY kode_promo DESC"

        await cursor.execute(q1)

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
async def getlastestiddetailpromokunjungan():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT detail_kode_promo FROM detail_promo_kunjungan WHERE detail_kode_promo LIKE 'DK%' ORDER BY detail_kode_promo DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_detail_kodepromo_kunjungan = items[0] if items is not None else None
        if id_detail_kodepromo_kunjungan is None:
          num = "1"
          strpad = "DK" + num.zfill(3)
        else:
          getNum = id_detail_kodepromo_kunjungan[2:]
          num = int(getNum) + 1
          strpad = "DK" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  

@app.post('/daftarpromokunjungan')
async def postpromokunjungan(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()
          lastidpromo = await getlastestidpromo()
          lastiddetailpromo = await getlastestiddetailpromokunjungan()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO promo(kode_promo,nama_promo,detail_kode_promo) VALUES(%s, %s, %s)"
          await cursor.execute(q1, (data['kode_promo'],data['nama_promo'],lastiddetailpromo))

          q2 = "INSERT INTO detail_promo_kunjungan(detail_kode_promo,limit_kunjungan,limit_promo,durasi,discount,harga_promo) VALUES(%s,%s,%s,%s,%s,%s)"
          await cursor.execute(q2, (lastiddetailpromo,data['limit_kunjungan'],data['limit_promo'],data['durasi'],data['discount'],data['harga_promo']))
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

async def getlastestiddetailpromotahunan():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT detail_kode_promo FROM detail_promo_tahunan WHERE detail_kode_promo LIKE 'DT%' ORDER BY detail_kode_promo DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_detail_kodepromo_tahunan = items[0] if items is not None else None
        if id_detail_kodepromo_tahunan is None:
          num = "1"
          strpad = "DT" + num.zfill(3)
        else:
          getNum = id_detail_kodepromo_tahunan[2:]
          num = int(getNum) + 1
          strpad = "DT" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  

@app.post('/daftarpromotahunan')
async def postpromotahunan(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()
          lastidpromo = await getlastestidpromo()
          lastiddetailpromotahunan = await getlastestiddetailpromotahunan()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO promo(kode_promo,nama_promo,kode_detail_promo) VALUES(%s, %s, %s)"
          await cursor.execute(q1, (data['kode_promo'],data['nama_promo'],lastiddetailpromotahunan))

          q2 = "INSERT INTO detail_promo_tahunan(detail_kode_promo,jangka_tahun,harga_promo) VALUES(%s,%s,%s)"
          await cursor.execute(q2, (lastiddetailpromotahunan,data['jangka_tahun'],data['harga_promo']))
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
