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
from jwt_auth import access_security, refresh_security

app = APIRouter()

@app.get('/user')
async def fnUser(
  user: JwtAuthorizationCredentials = Security(access_security)
) :
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          query = """
            SELECT u.*, k.nama_karyawan, k.jabatan FROM users u 
            INNER JOIN karyawan k ON u.id_karyawan = k.id_karyawan
            WHERE u.id_karyawan = %s
          """
          await cursor.execute(query, (user['id_karyawan'], ))

          column_name = []
          for kol in cursor.description:
            column_name.append(kol[0])
          
          items = await cursor.fetchall()

          #Buat bentuk df
          df = pd.DataFrame(items, columns=column_name)

          # Jadikan json
          subject = df.to_dict('records')[0] # pecahkan arraynya

          # Pop password
          subject.pop('passwd', None)

          return subject
        except aiomysqlerror as e:
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
  
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)

@app.post('/login')
async def login(
  request: Request
) :
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          data = await request.json()
          passwd = data['passwd']

          # Query Login
          query = """
            SELECT u.*, k.nama_karyawan, k.jabatan FROM users u 
            INNER JOIN karyawan k ON u.id_karyawan = k.id_karyawan
            WHERE u.id_karyawan = %s
          """ 
          await cursor.execute(query, (data['id_karyawan'], ))

          column_names = []
          for kol in cursor.description:
            column_names.append(kol[0])

          # Pake await fetchone, krn hanya mw ambil 1 baris data. klo mw baanyak make fetchall
          items = await cursor.fetchone()

          # Jika ga ad data
          if not items:
            raise HTTPException(status_code=404, detail="User Not Found")
          
          # berdasarkan db, attr passwd di index ke-1
          stored_pass = items[1]

          if passwd != stored_pass:
            raise HTTPException(status_code=401, detail="Password Salah")
          
          # Buat Dataframe utk dapatin data dalam bentuk map/json
          # kalo items hanya return single row, lapis make [] krn pake fetchone, klo fetchall g ush lapis.
          df = pd.DataFrame([items], columns=column_names)

          # utk return data. ambil index ke-0 krn dia return dalam bentuk list/array
          subject = df.to_dict('records')[0]
          # Hilangin Kolom Passwd utk jaga privasi pas return
          subject.pop('passwd', None)
          subject.pop('created_at', None)
          subject.pop('updated_at', None)

          # Buat Token. penghubung antara frontend dan backend
          access_token = access_security.create_access_token(subject)
          refresh_token = refresh_security.create_refresh_token(subject)

          return {
            "data_user": subject,
            "access_token" : access_token,
            "refresh_token" : refresh_token,
          }

        except HTTPException as e:
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)