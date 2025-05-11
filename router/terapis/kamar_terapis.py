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

# Bagian OB
@app.get('/data_ob')
async def getData():
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # Query 
          query = """
            SELECT u.*, h.nama_hakakses, k.nama_karyawan FROM users u 
            INNER JOIN hak_akses h ON u.hak_akses = h.id
            LEFT JOIN karyawan k ON u.id_karyawan = k.id_karyawan
            WHERE u.hak_akses = %s
          """ 
          await cursor.execute(query, ('9', ))

          column_names = []
          for kol in cursor.description:
            column_names.append(kol[0])

          # Pake await fetchone, krn hanya mw ambil 1 baris data. klo mw baanyak make fetchall
          items = await cursor.fetchall()

          # Jika ga ad data
          if not items:
            raise HTTPException(status_code=404, detail="User Not Found")
          
          # Buat Dataframe utk dapatin data dalam bentuk map/json
          # kalo items hanya return single row, lapis make [] krn pake fetchone, klo fetchall g ush lapis.
          df = pd.DataFrame(items, columns=column_names)

          # utk return data. ambil index ke-0 krn dia return dalam bentuk list/array
          subject = df.to_dict('records')
          for item in subject:
            item.pop('passwd', None)

          return subject

        except HTTPException as e:
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  

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
# End Bagian OB

@app.get("/latest_trans")
async def getLatestTrans(
  user: JwtAuthorizationCredentials = Security(access_security)
):
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # Query Paket
          q_paket = """
            SELECT dtpa.id_paket, pm.nama_paket_msg, dtpa.durasi_awal, 
            dtpa.total_durasi, pm.detail_paket as deskripsi_paket, m.id_transaksi,
            m.created_at as tgl_transaksi, m.id_terapis, k.nama_karyawan, r.nama_ruangan
            FROM detail_transaksi_paket dtpa 
            INNER JOIN main_transaksi m ON dtpa.id_detail_transaksi = m.id_detail_transaksi
            INNER JOIN karyawan k ON m.id_terapis = k.id_karyawan
            LEFT JOIN ruangan r ON m.id_ruangan = r.id_ruangan
            LEFT JOIN paket_massage pm ON dtpa.id_paket = pm.id_paket_msg
            WHERE m.id_ruangan = %s AND m.sedang_dikerjakan = FALSE
            ORDER BY m.created_at DESC
          """ 
          # id karyawan disini adlh id akun yg login. berarti id ruangan.
          await cursor.execute(q_paket, (user['id_ruangan'], ))

          column_names = []
          for kol in cursor.description:
            column_names.append(kol[0])

          items = await cursor.fetchall()

          # kalo items hanya return single row, lapis make [] krn pake fetchone, klo fetchall g ush lapis.
          df = pd.DataFrame(items, columns=column_names)

          # utk return data. ambil index ke-0 krn dia return dalam bentuk list/array
          subject = df.to_dict('records')

          # End Query Paket

          # Start Query Produk
          q_produk = """
            SELECT dtpa.id_produk, mp.nama_produk, dtpa.durasi_awal, 
            dtpa.total_durasi, m.id_transaksi,
            m.created_at as tgl_transaksi, m.id_terapis, k.nama_karyawan, r.nama_ruangan
            FROM detail_transaksi_produk dtpa 
            INNER JOIN main_transaksi m ON dtpa.id_detail_transaksi = m.id_detail_transaksi
            INNER JOIN karyawan k ON m.id_terapis = k.id_karyawan
            LEFT JOIN ruangan r ON m.id_ruangan = r.id_ruangan
            LEFT JOIN menu_produk mp ON dtpa.id_produk = mp.id_produk
            WHERE m.id_ruangan = %s AND m.sedang_dikerjakan = FALSE
            ORDER BY m.created_at DESC
          """ 
          # id karyawan disini adlh id akun yg login. berarti id ruangan.
          await cursor.execute(q_produk, (user['id_ruangan'], ))

          column_names = []
          for kol in cursor.description:
            column_names.append(kol[0])

          items2 = await cursor.fetchall()

          # kalo items hanya return single row, lapis make [] krn pake fetchone, klo fetchall g ush lapis.
          df2 = pd.DataFrame(items2, columns=column_names)
          # utk return data. ambil index ke-0 krn dia return dalam bentuk list/array
          subject2 = df2.to_dict('records')

          return {
            "data_paket": subject,
            "data_produk": subject2
          }

        except HTTPException as e:
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  

  
  
