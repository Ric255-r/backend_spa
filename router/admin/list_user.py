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

app = APIRouter(
  prefix="/listuser",
)

@app.get('/')
async def getDataUser():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = """
          SELECT u.*, h.nama_hakakses, k.nama_karyawan FROM users u 
          INNER JOIN hak_akses h ON u.hak_akses = h.id
          LEFT JOIN karyawan k ON u.id_karyawan = k.id_karyawan
        """
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data User": str(e)}, status_code=500)
  

@app.put('/update_user/{id_karyawan}')
async def updateUser(
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

          if "new_pass" in data and data['new_pass'] is not None:
            q1 = "UPDATE users SET passwd = %s WHERE id_karyawan = %s"
            await cursor.execute(q1, (data['new_pass'], id_karyawan)) 

          hak_akses_tambahan = data.get('secondary_hakakses', [])

          # Delete dl Bru Insert
          q2 = "DELETE FROM karyawan_hakakses_tambahan WHERE id_karyawan = %s"
          await cursor.execute(q2, (id_karyawan, )) 

          for item in hak_akses_tambahan:
            q3 = "INSERT INTO karyawan_hakakses_tambahan(id_karyawan, id_hak_akses) VALUES(%s, %s)"
            await cursor.execute(q3, (id_karyawan, item)) 

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
  

@app.delete('/delete_user/{id_karyawan}')
async def deleteUser(
  id_karyawan: str,
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # Delete dl Bru Insert
          q2 = "DELETE FROM users WHERE id_karyawan = %s"
          await cursor.execute(q2, (id_karyawan, )) 

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