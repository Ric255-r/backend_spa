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
  prefix="/listroom",
)

@app.get('/dataroom')
async def getDataRoom():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT * FROM ruangan ORDER BY nama_ruangan ASC"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)
  

@app.put('/update_room/{id_ruangan}')
async def putRuangan(
  id_ruangan: int,
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
          await cursor.execute("SELECT * FROM ruangan WHERE id_ruangan = %s", (id_ruangan,))
          exists = await cursor.fetchone()

          if not exists:
              await conn.rollback()
              return JSONResponse(content={"status": "Error", "message": "Id Ruangan not found"}, status_code=404)
          
          q1 = "UPDATE ruangan SET nama_ruangan = %s, lantai = %s, jenis_ruangan = %s, status = %s, harga_ruangan = %s WHERE id_ruangan = %s"
          await cursor.execute(q1, (data['nama_ruangan'], data['lantai'], data['jenis_ruangan'], data['status'], data['harga_ruangan'], id_ruangan)) 
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
  
@app.delete('/delete_room/{id_ruangan}')
async def deleteRoom(
  id_ruangan: int,
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
          # 2. Execute querynya
          data = await request.json()
          q1 = "SELECT id_karyawan FROM ruangan WHERE id_ruangan = %s"
          await cursor.execute(q1, (id_ruangan))
          items = await cursor.fetchone()

          id_karyawan = items[0]

          q2 = "DELETE FROM ruangan WHERE id_ruangan = %s"
          await cursor.execute(q2, (id_ruangan))

          q3 = "DELETE FROM users WHERE id_karyawan = %s"
          await cursor.execute(q3, (id_karyawan))
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