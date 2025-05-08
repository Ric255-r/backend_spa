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
          q1 = "INSERT INTO ruangan (nama_ruangan, id_karyawan, lantai, jenis_ruangan, status) VALUES(%s, %s, %s, %s, %s)"
          await cursor.execute(q1, (data['nama_ruangan'], data['kode_ruangan'],data['lantai'], data['jenis_ruangan'], data['status'])) 
          q2 = "INSERT INTO users (id_karyawan, passwd, hak_akses) VALUES(%s, %s, %s)"
          await cursor.execute(q2, (data['kode_ruangan'], data['passwd'], data['hak_akses']))

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
    
@app.get('/idroom')
async def getIdRoom():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = """
             SELECT MAX(CAST(SUBSTRING(id_karyawan, 3) AS UNSIGNED)) 
                FROM ruangan 
                WHERE id_karyawan LIKE 'KT%'
             """

        await cursor.execute(q1)
        last_id = (await cursor.fetchone())[0] or 0

        next_id = last_id + 1

        formatted_id = f"KT{next_id:03d}"
        # items = await cursor.fetchall()
        return formatted_id

  except Exception as e:
    return JSONResponse({"Error Get Data ID Room": str(e)}, status_code=500)
  
  # column_name = []
  #       for kol in cursor.description:
  #         column_name.append(kol[0])

  #       df = pd.DataFrame(items, columns=column_name)
  #       return df.to_dict('records')