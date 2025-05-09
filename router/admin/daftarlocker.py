from typing import Optional

import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror

app = APIRouter(prefix=("/locker"))

@app.get('/getlastnolocker')
async def getlastestnolocker():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        q1 = "SELECT nomor_locker FROM data_loker ORDER BY CAST(nomor_locker AS UNSIGNED) DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        nomor_locker = items[0] if items is not None else None

        if nomor_locker is None:
          num = "1"
          strpad = num
        else:
          num = int(nomor_locker) + 1
          strpad = num

        return strpad
  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)

@app.post('/daftarlocker')
async def daftarlocker(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()
          lastnomorlocker = await getlastestnolocker()

          # 2. Execute querynya
          q1 = "INSERT INTO data_loker(nomor_locker,status) VALUES(%s,%s)"
          await cursor.execute(q1, (lastnomorlocker,0))

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