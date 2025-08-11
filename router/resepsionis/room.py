from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror
import asyncio

app = APIRouter(prefix=("/ruangan"))

@app.get('/getdataruangan')
async def getdataruangan() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = "SELECT a.nama_ruangan, a.status,COALESCE(b.sum_durasi_menit, 0) AS sum_durasi_menit, COALESCE(b.kode_ruangan, 'Tidak Ada') AS kode_ruangan FROM ruangan a left join durasi_kerja_sementara b ON a.id_karyawan = b.kode_ruangan ORDER BY a.nama_ruangan asc"

        await cursor.execute(q1)  

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)

@app.put('/updateruangan')
async def updatelocker(
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
          q1 = "UPDATE ruangan SET status = %s WHERE id_ruangan= %s"
          await cursor.execute(q1, (data['status'],data['id_ruangan']))
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

@app.get('/getstatus')
async def getstatus(
    request : Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        data = await request.json()
        q1 = "SELECT jenis_ruangan FROM ruangan where nama_ruangan = %s "

        await cursor.execute(q1, (data['nama_ruangan'],))  

        status = await cursor.fetchall()

        jenis_ruangan = status[0][0] if status else None

        print('status')

        if jenis_ruangan == "VIP" :
          q2 = "SELECT harga_vip FROM harga_vip"

          await cursor.execute(q2)
          hargavip = await cursor.fetchall()

        else :
          hargavip = [(0,)]

      df = pd.DataFrame(hargavip, columns=["hargavip"])
      return df.to_dict('records')

  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)

@app.get('/datahargavip')
async def getDataHargaVip():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT harga_vip FROM harga_vip"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)
  
@app.put('/updatehargavip')
async def updatehargavip(
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
          q1 = "UPDATE harga_vip SET harga_vip = %s WHERE id = 1"
          await cursor.execute(q1, (data['harga_baru_vip']))
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