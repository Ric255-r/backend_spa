from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Query, Request, HTTPException, Security, UploadFile
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
  prefix="/form_user",
)

@app.get('/hak_akses')
async def getHakAkses(
  id: Optional[int] = Query(None),
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        if id is None:
          q1 = "SELECT id, nama_hakakses FROM hak_akses"
          await cursor.execute(q1)
        else:
          q1 = "SELECT id, nama_hakakses FROM hak_akses WHERE id != %s"
          await cursor.execute(q1, (id, ))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Tabel Hak Akses": str(e)}, status_code=500)
  

@app.get('/kode')
async def getKodeKaryawan():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT id_karyawan, nama_karyawan FROM karyawan"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Kode Karyawan": str(e)}, status_code=500)
  
@app.post('/post_users')
async def postUsers(
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

          q1 = "INSERT INTO users(id_karyawan, passwd, hak_akses) VALUES(%s, %s, %s)"
          await cursor.execute(q1, (data['id_karyawan'], data['passwd'], data['hak_akses'])) 

          hak_akses_tambahan = data.get('hak_akses_tambahan', [])
          for item in hak_akses_tambahan:
            q2 = "INSERT INTO karyawan_hakakses_tambahan(id_karyawan, id_hak_akses) VALUES(%s, %s)"
            await cursor.execute(q2, (data['id_karyawan'], item)) 

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