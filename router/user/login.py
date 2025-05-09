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
            SELECT u.id_karyawan, u.passwd, h.nama_hakakses AS hak_akses, 
            k.nama_karyawan, k.jabatan 
            FROM users u 
            INNER JOIN hak_akses h ON u.hak_akses = h.id
            LEFT JOIN karyawan k ON u.id_karyawan = k.id_karyawan
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
          records = df.to_dict('records')

          if not records:
            return JSONResponse(
              content={"status": "error", "message": "Data tidak ditemukan"},
              status_code=404
            )

          subject = records[0]

          # Jika hak akses user adalah ruangan. tambahkan keyvalue lagi
          if user['hak_akses'] == "ruangan":
            subject['id_ruangan'] = user['id_ruangan']
            # sesuaikan dengan /login, 
            subject['id_akun_ruangan'] = user['id_akun_ruangan']
            subject['nama_ruangan'] = user['nama_ruangan']
            subject['lantai'] = user['lantai']
            subject['jenis_ruangan'] = user['jenis_ruangan']
            subject['status'] = user['status']

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

          # Query Login. Tambah Isolation Level
          await cursor.execute("SET autocommit = 1;")
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

          """
            If you're still having issues, you can close and reopen the cursor before your SELECT query 
            (this forces MySQL to discard old session state):
            await cursor.close()
            cursor = await conn.cursor()
          """

          query = """
            SELECT u.id_karyawan, u.passwd, h.nama_hakakses AS hak_akses, 
            k.nama_karyawan, k.jabatan 
            FROM users u 
            INNER JOIN hak_akses h ON u.hak_akses = h.id
            LEFT JOIN karyawan k ON u.id_karyawan = k.id_karyawan
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

          if subject['hak_akses'].lower() == "ruangan":
            query2 = """
              SELECT * FROM ruangan WHERE id_karyawan = %s LIMIT 1
            """ 
            await cursor.execute(query2, (subject['id_karyawan'], ))

            # Pake await fetchone, krn hanya mw ambil 1 baris data. klo mw baanyak make fetchall
            items2 = await cursor.fetchone()
            # print(items2)

            # Masukin Data dari tabel ruangan utk login
            subject['id_ruangan'] = items2[0]
            subject['id_akun_ruangan'] = items2[1]
            subject['nama_ruangan'] = items2[2]
            subject['lantai'] = items2[3]
            subject['jenis_ruangan'] = items2[4]
            subject['status'] = items2[5] 

            # Buat Token. penghubung antara frontend dan backend
            # Terpaksa ku buat di blok if dan else. terkesan redudant. tapi begini jalan
            # klo cmn if doang, dia ga ke store data tambahannya
            access_token = access_security.create_access_token(subject)
            refresh_token = refresh_security.create_refresh_token(subject)
          else:
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
  
@app.get('/hak_akses')
async def hak_akses(
  user: JwtAuthorizationCredentials = Security(access_security)
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # Query Hak Akses 1 (Utama)
          q1 = """
            SELECT u.*, h.nama_hakakses FROM users u 
            INNER JOIN hak_akses h ON u.hak_akses = h.id
            WHERE u.id_karyawan = %s
          """
          await cursor.execute(q1, (user['id_karyawan'], ))

          column_name = []
          for kol in cursor.description:
            column_name.append(kol[0])
          
          items = await cursor.fetchall()

          #Buat bentuk df
          df = pd.DataFrame(items, columns=column_name)

          # Jadikan json
          records = df.to_dict('records')
          subject = records[0]
          # Pop password
          subject.pop('passwd', None)

          if not records:
            return JSONResponse(
              content={"status": "error", "message": "Data tidak ditemukan"},
              status_code=404
            )
          # End Query 1

          # Query Hak Akses Tambahan
          q2 = """
            SELECT kht.*, h.nama_hakakses FROM karyawan_hakakses_tambahan kht 
            INNER JOIN hak_akses h ON kht.id_hak_akses = h.id 
            LEFT JOIN users u ON kht.id_karyawan = u.id_karyawan 
            WHERE kht.id_karyawan = %s;
          """
          await cursor.execute(q2, (user['id_karyawan'], ))

          column_name = []
          for kol in cursor.description:
            column_name.append(kol[0])
          
          items = await cursor.fetchall()

          #Buat bentuk df
          df2 = pd.DataFrame(items, columns=column_name)
          records2 = df2.to_dict('records')
          # masukin hasil records 2 ke records 1
          subject['second_hakakses'] = records2
          # End Query Hak Akses Tambahan

          return subject
        except aiomysqlerror as e:
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
  
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
