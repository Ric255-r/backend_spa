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
  prefix="/pekerja",
)
    
@app.get('/getIdKaryawan/{jabatan}')
async def getIdKaryawan(jabatan: str):  # Accept 'category' as a parameter
    try:
        pool = await get_db()  # Get the database connection pool

        # Map the categories to their prefixes
        prefix_mapping = {
            "Terapis": "T",
            "Resepsionis": "R",
            "Supervisor": "S",
            "Office Boy": "O",
            "Admin": "A",
            "Kitchen": "K",
            "GRO": "G",
        }

        # Get the prefix for the selected category
        prefix = prefix_mapping.get(jabatan)
        if not prefix:
            return JSONResponse({"error": "Invalid category"}, status_code=400)

        async with pool.acquire() as conn:  # Auto release connection
            async with conn.cursor() as cursor:
                await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
                # Query the latest ID for the given category
                query = f"""
                SELECT id_karyawan 
                FROM karyawan 
                WHERE id_karyawan LIKE '{prefix}%' 
                ORDER BY id_karyawan DESC 
                LIMIT 1
                """
                await cursor.execute(query)

                result = await cursor.fetchone()
                latest_id = result[0] if result else None

                # Generate the next ID
                if latest_id is None:
                    new_id = f"{prefix}001"  # Start from 001 if no existing records
                else:
                    num = int(latest_id[1:]) + 1  # Extract number, increment
                    new_id = f"{prefix}{str(num).zfill(3)}"  # Zero-pad to 3 digits

                return new_id

    except Exception as e:
        return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)

@app.post('/post_pekerja')
async def postPekerja(
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
          q1 = "INSERT INTO karyawan (id_karyawan, nik, nama_karyawan, alamat, umur, jk, no_hp, jabatan, kontrak_img) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
          await cursor.execute(q1, (data['id_karyawan'], data['nik'], data['nama_karyawan'], data['alamat'], data['umur'], data['jk'], data['no_hp'], data['jabatan'], data['kontrak_img'])) 
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
  
@app.post('/post_ob')
async def postOb(
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
          q1 = "INSERT INTO karyawan (id_karyawan, nik, nama_karyawan, alamat, umur, jk, no_hp, jabatan, kontrak_img) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
          await cursor.execute(q1, (data['id_karyawan'], data['nik'], data['nama_karyawan'], data['alamat'], data['umur'], data['jk'], data['no_hp'], data['jabatan'], data['kontrak_img'])) 
          q2 = "INSERT INTO hari_kerja_ob (kode_ob, senin, selasa, rabu, kamis, jumat, sabtu, minggu) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
          await cursor.execute(q2, (data['id_karyawan'], data['senin'], data['selasa'], data['rabu'], data['kamis'], data['jumat'], data['sabtu'], data['minggu']))
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
  
@app.post('/post_terapis')
async def postTerapis(
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
          q1 = "INSERT INTO karyawan (id_karyawan, nik, nama_karyawan, alamat, umur, jk, no_hp, jabatan, kontrak_img) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
          await cursor.execute(q1, (data['id_karyawan'], data['nik'], data['nama_karyawan'], data['alamat'], data['umur'], data['jk'], data['no_hp'], data['jabatan'], data['kontrak_img'])) 
          q2 = "INSERT INTO hari_kerja_terapis (kode_terapis, senin, selasa, rabu, kamis, jumat, sabtu, minggu) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
          await cursor.execute(q2, (data['id_karyawan'], data['senin'], data['selasa'], data['rabu'], data['kamis'], data['jumat'], data['sabtu'], data['minggu']))
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

# async def getIdKaryawan():
#   try:
#     pool = await get_db() # Get The pool

#     async with pool.acquire() as conn:  # Auto Release
#       async with conn.cursor() as cursor:

#         q1 = "SELECT id_karyawan FROM karyawan"
#         await cursor.execute(q1)

#         items = await cursor.fetchone() #id transaksi terletak di index ke-0
#         id_karyawan = items[0] if items is not None else None

#         if id_karyawan is None:
#           num = "1"
#           strpad = "P" + num.zfill(3)
#         else:
#           getNum = id_produk[1:]
#           num = int(getNum) + 1
#           strpad = "P" + str(num).zfill(3)

#         return strpad


#   except Exception as e:
#     return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)