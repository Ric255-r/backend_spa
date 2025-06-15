import os
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Path, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from urllib.parse import unquote
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
from fastapi.responses import FileResponse
from fastapi import HTTPException
import pandas as pd
from aiomysql import Error as aiomysqlerror

KONTRAK_DIR = os.path.abspath("kontrak")

app = APIRouter(
  prefix="/listpekerja",
)

@app.get('/datapekerja')
async def getDataPekerja():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT * FROM karyawan"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Karyawan": str(e)}, status_code=500)
  
# Ini Utk transaksi
@app.get('/dataterapis')
async def getDataTerapis():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT * FROM karyawan WHERE (jabatan = %s or id_karyawan LIKE %s) AND status = 'aktif'"
        await cursor.execute(q1, ("terapis", "T%"))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Terapis": str(e)}, status_code=500)
  
@app.get('/dataterapisrolling')
async def getDataTerapisRolling():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT k.*, a.jam_absen FROM karyawan k JOIN absensi_terapis a ON k.id_karyawan = a.id_karyawan WHERE k.jabatan = %s OR k.id_karyawan LIKE %s ORDER BY a.jam_absen ASC;"
        await cursor.execute(q1, ("terapis", "T%"))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Terapis": str(e)}, status_code=500)
  
@app.get('/datagro')
async def getDataGro():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT * FROM karyawan WHERE jabatan = %s or id_karyawan LIKE %s"
        await cursor.execute(q1, ("gro", "G%"))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data GRO": str(e)}, status_code=500)

# End Utk Transaksi

@app.put('/update_pekerja/{id_karyawan}')
async def putPekerja(
  id_karyawan: str,
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
          # await cursor.execute("SELECT FROM karyawan WHERE id_karyawan = %s", (data['id_karyawan'],))
          # exists = await cursor.fetchone()

          # if not exists:
          #     await conn.rollback()
          #     return JSONResponse(content={"status": "Error", "message": "Karyawan not found"}, status_code=404)
          
          q1 = "UPDATE karyawan SET nik = %s, nama_karyawan = %s, alamat = %s, jk = %s, no_hp = %s, status = %s WHERE id_karyawan = %s"
          await cursor.execute(q1, (data['nik'], data['nama_karyawan'], data['alamat'], data['jk'], data['no_hp'], data['status'], id_karyawan)) 
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return JSONResponse(content={"status": "Success", "message": "Data Berhasil Diupdate"}, status_code=200)
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
  
@app.delete('/delete_pekerja/{id_karyawan}')
async def deletePekerja(
  id_karyawan: str,
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
          
          q1 = "DELETE FROM karyawan WHERE id_karyawan = %s"
          await cursor.execute(q1, (id_karyawan)) 
          q2 = "DELETE FROM users WHERE id_karyawan = %s"
          await cursor.execute(q2, (id_karyawan))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return JSONResponse(content={"status": "Success", "message": "Data Berhasil Dihapus"}, status_code=200)
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

@app.get('/caripekerja')
async def cariPekerja(
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
          q1 = "SELECT * FROM karyawan WHERE nama_karyawan LIKE %s"
          await cursor.execute(q1, (data['nama_karyawan'])) 
          # 3. Klo Sukses, dia bkl save ke db
          
          items = await cursor.fetchall()

          column_name = []
          for kol in cursor.description:
            column_name.append(kol[0])

          df = pd.DataFrame(items, columns=column_name)
          return df.to_dict('records')

          return JSONResponse(content={"status": "Success", "message": "Data Berhasil Dicari"}, status_code=200)
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



