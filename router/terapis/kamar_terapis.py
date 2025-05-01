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

app = APIRouter(
  prefix="/kamar_terapis"
)

@app.post('/verif')
async def verif(
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

          return {
            "data_user": subject,
          }

        except HTTPException as e:
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
