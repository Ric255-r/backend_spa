from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
import pandas as pd
from aiomysql import Error as aiomysqlerror

app = APIRouter()

async def buatSelect(
  conn, cursor
) :
  q1 = "SELECT * FROM table_test"
  await cursor.execute(q1)

  items = await cursor.fetchall()

  column_name = []
  for kol in cursor.description:
    print(cursor.description)
    column_name.append(kol[0])

  df = pd.DataFrame(items, columns=column_name)
  print(df)
  aa = df.to_dict('records')
  print(aa)
  return aa

# Syntax ini aman dari RC
@app.get("/testing")
async def testing():
  try:
    pool = await get_db() # Get The pool

    # Alvin suka makan pisang goreng. versi 2 lebih OP. tes alvin
    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        return await buatSelect(conn, cursor)
  except HTTPException as e:
    return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
 # No `finally` needed! Pool handles cleanup.

@app.post('/testing')
async def postTest(
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
          q1 = "INSERT INTO table_test(nama_barang, harga, ket) VALUES(%s, %s, %s)"
          await cursor.execute(q1, (data['nama_barang'], int(data['harga']), data['ket'], ))

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return await buatSelect(conn,cursor)
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
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)


@app.delete('/testing/{id}/{namabarang}')
async def deleteTest(
  id : str,
  namabarang : str,
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction

          # 2. Execute querynya
          q1 = "DELETE FROM table_test WHERE id = %s or nama_barang = %s"
          await cursor.execute(q1, (id,namabarang))

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return await buatSelect(conn,cursor)
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
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)
