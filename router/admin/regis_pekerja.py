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
  prefix="/room",
)

@app.post('/post_room')
async def postRoom(
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
          q1 = "INSERT INTO ruangan (nama_ruangan, lantai, jenis_ruangan, status) VALUES(%s, %s, %s, %s)"
          await cursor.execute(q1, (data['nama_ruangan'], data['lantai'], data['jenis_ruangan'], data['status'])) 

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

@app.get('/check_room/{nama_ruangan}')
async def check_room_name(nama_ruangan: str):
    try:
        print(nama_ruangan)
        # Validate input to ensure it is not empty or invalid
        if not nama_ruangan or nama_ruangan.strip() == "":
            return JSONResponse({"error": "Room name cannot be empty"}, status_code=400)

        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Check if nama_ruangan already exists in the table
                query = """
                        SELECT COUNT(*)
                        FROM ruangan
                        WHERE nama_ruangan = %s
                        """
                await cursor.execute(query, (nama_ruangan,))
                result = await cursor.fetchone()

                # Return whether the room name exists (even if it's not a primary key)
                exists = result[0] > 0
                return {"exists": exists}
    except Exception as e:
        print(f"Error in /check_room endpoint: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)