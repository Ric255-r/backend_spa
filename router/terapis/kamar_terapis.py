from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Query, Request, HTTPException, Security, UploadFile
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
from datetime import timedelta

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
  prev_route: Optional[str] = Query(None),
  user: JwtAuthorizationCredentials = Security(access_security)
):
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # Paksa Buat Cursor Baru
          await cursor.close()
          cursor = await conn.cursor()
          # End Paksa

          # Query Paket
          q_paket = f"""
            SELECT dtpa.id_paket, pm.nama_paket_msg, dtpa.durasi_awal, 
            dtpa.total_durasi, pm.detail_paket as deskripsi_paket, m.id_transaksi,
            m.created_at as tgl_transaksi, m.id_terapis, dtpa.id_detail_transaksi,
            k.nama_karyawan, r.nama_ruangan, r.id_karyawan AS kode_ruangan
            FROM detail_transaksi_paket dtpa 
            INNER JOIN main_transaksi m ON dtpa.id_transaksi = m.id_transaksi
            INNER JOIN karyawan k ON m.id_terapis = k.id_karyawan
            LEFT JOIN ruangan r ON m.id_ruangan = r.id_ruangan
            LEFT JOIN paket_massage pm ON dtpa.id_paket = pm.id_paket_msg
            WHERE m.id_ruangan = %s AND m.sedang_dikerjakan = {'FALSE' if prev_route is None else 'TRUE'}
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
          q_produk = f"""
            SELECT dtpa.id_produk, mp.nama_produk, dtpa.durasi_awal, 
            dtpa.total_durasi, m.id_transaksi,
            m.created_at as tgl_transaksi, m.id_terapis, dtpa.id_detail_transaksi, 
            k.nama_karyawan, r.nama_ruangan, r.id_karyawan AS kode_ruangan
            FROM detail_transaksi_produk dtpa 
            INNER JOIN main_transaksi m ON dtpa.id_transaksi = m.id_transaksi
            INNER JOIN karyawan k ON m.id_terapis = k.id_karyawan
            LEFT JOIN ruangan r ON m.id_ruangan = r.id_ruangan
            LEFT JOIN menu_produk mp ON dtpa.id_produk = mp.id_produk
            WHERE m.id_ruangan = %s AND m.sedang_dikerjakan = {'FALSE' if prev_route is None else 'TRUE'}
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
        
        finally:
          if cursor:
            await cursor.close()
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
@app.delete('/delete_progress')
async def delete_progress(
  id_transaksi: str = Query(),
  id_terapis: str = Query()
):
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()
          # Query 
          query = """
            DELETE FROM terapis_kerja WHERE id_transaksi = %s AND id_terapis = %s
          """ 
          await cursor.execute(query, (id_transaksi, id_terapis))

          query2 = """
            DELETE FROM durasi_kerja_sementara WHERE id_transaksi = %s
          """ 
          await cursor.execute(query2, (id_transaksi, ))

          query3 = "UPDATE main_transaksi SET sedang_dikerjakan = 0 WHERE id_transaksi = %s"
          await cursor.execute(query3, (id_transaksi, ))

          await conn.commit()

        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  

# @app.get('/get_data_trans/{id_transaksi}')
# async def getData(
#   id_transaksi: str,
# ) :
#   try: 
#     pool = await get_db()

#     async with pool.acquire() as conn:
#       async with conn.cursor() as cursor:
#         try:
#           q1 = """
#             SELECT id_detail_transaksi, id_ruangan, id_terapis 
#             FROM main_transaksi WHERE id_transaksi = %s
#           """ 
#           await cursor.execute(q1, (id_transaksi, ))

#           items = await cursor.fetchone()
#           id_detail_transaksi = items[0]
#           id_ruangan = items[1]
#           id_terapis = items[2]

#           q2 = """
#             SELECT nama_ruangan FROM ruangan 
#           """

#           # Query 2
#           q2 = """
#             SELECT * FROM detail_transaksi_produk WHERE id_detail_transaksi = %s
#           """
#           await cursor.execute(q2, (id_detail_transaksi, ))

#           column_names2 = []
#           for kol in cursor.description:
#             column_names2.append(kol[0])

#           items2 = await cursor.fetchall()

#           df2 = pd.DataFrame(items2, columns=column_names2)
#           # utk return data. 
#           subject2 = df2.to_dict('records')

#           # Query 3
#           q2 = """
#             SELECT * FROM detail_transaksi_paket WHERE id_detail_transaksi = %s
#           """
#           await cursor.execute(q2, (id_detail_transaksi, ))

#           column_names3 = []
#           for kol in cursor.description:
#             column_names3.append(kol[0])

#           items3 = await cursor.fetchall()

#           df3 = pd.DataFrame(items3, columns=column_names3)
#           # utk return data. 
#           subject3 = df3.to_dict('records')

#           return {
#             "data_produk" :subject2,
#             "data_paket": subject3,
#             "id_ruangan": id_ruangan,
#             "id_terapis": id_terapis
#           }

#         except HTTPException as e:
#           await conn.rollback()
#           return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

#         except aiomysqlerror as e:
#           await conn.rollback()
#           return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
#   except Exception as e:
#     return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
@app.get('/get_remaining_time')
async def remainingTime(
  id_transaksi: str = Query()
):
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await cursor.execute("SET autocommit = 1;")
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
          # Query 
          query = """
            SELECT dks.sum_durasi_menit, TIME_FORMAT(tk.jam_mulai, '%%H:%%i:%%s') AS jam_mulai 
            FROM durasi_kerja_sementara dks
            LEFT JOIN terapis_kerja tk ON dks.id_transaksi = tk.id_transaksi
            WHERE dks.id_transaksi = %s
          """ 
          await cursor.execute(query, (id_transaksi, ))

          # Pake await fetchone, krn hanya mw ambil 1 baris data. klo mw baanyak make fetchall
          items = await cursor.fetchone()

          return items if items else []

        except HTTPException as e:
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)

@app.post('/ins_datang')
async def insert_datang(
  request: Request,
) :
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()

          try:
            jam_datang = datetime.strptime(data['jam_datang'], '%H:%M:%S').time()
          except ValueError:
            return JSONResponse(
              content={"status": "error", "message": "Invalid time format, use HH:MM:SS"},
              status_code=400
            )
          
          qCheck = """
            SELECT * FROM terapis_kerja WHERE id_transaksi = %s AND id_terapis = %s
          """
          await cursor.execute(qCheck, (data['id_transaksi'], data['id_terapis']))
          items = await cursor.fetchone()

          if not items:
            q1 = "INSERT INTO terapis_kerja(id_transaksi, id_terapis, jam_datang) VALUES(%s, %s, %s)"
            await cursor.execute(q1, (data['id_transaksi'], data['id_terapis'], jam_datang))

            await conn.commit()

        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  

@app.put('/update_mulai')
async def update_mulai(
  request: Request,
  user: JwtAuthorizationCredentials = Security(access_security)
) :
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()

          try:
            jam_mulai = datetime.strptime(data['jam_mulai'], '%H:%M:%S').time()
          except ValueError:
            return JSONResponse(
              content={"status": "error", "message": "Invalid time format, use HH:MM:SS"},
              status_code=400
            )
          
          qCheckTerapis = """
            SELECT 1 FROM terapis_kerja 
            WHERE id_transaksi = %s AND id_terapis = %s AND is_tunda = TRUE
          """
          await cursor.execute(qCheckTerapis, (data['id_transaksi'], data['id_terapis']))
          isTunda = await cursor.fetchone()

          if isTunda:
            qUnpause = """
              UPDATE terapis_kerja 
              SET is_tunda = FALSE 
              WHERE id_transaksi = %s AND id_terapis = %s
            """
            await cursor.execute(qUnpause, (data['id_transaksi'], data['id_terapis']))
          else:
            qUpdateMulai = """
              UPDATE terapis_kerja 
              SET jam_mulai = %s 
              WHERE id_transaksi = %s AND id_terapis = %s
            """
            await cursor.execute(qUpdateMulai, (jam_mulai, data['id_transaksi'], data['id_terapis']))


          q2 = "UPDATE main_transaksi SET sedang_dikerjakan = 1 WHERE id_transaksi = %s"
          await cursor.execute(q2, (data['id_transaksi'], ))

          qCheck = """
            SELECT * FROM durasi_kerja_sementara WHERE id_transaksi = %s
          """
          await cursor.execute(qCheck, (data['id_transaksi'], ))
          items = await cursor.fetchone()

          # Jika ga ad data
          if not items:
            q3 = """
              INSERT INTO durasi_kerja_sementara(kode_ruangan, id_transaksi, sum_durasi_menit)
              VALUES(%s, %s, %s)
            """
            await cursor.execute(q3, (user['id_akun_ruangan'], data['id_transaksi'], data['sum_durasi_menit']))

          await conn.commit()
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
@app.put('/tunda')
async def tunda(
  request: Request,
) :
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()

          q1 = "UPDATE terapis_kerja SET is_tunda = TRUE WHERE id_transaksi = %s"
          await cursor.execute(q1, (data['id_transaksi'], ))

          q2 = "UPDATE main_transaksi SET sedang_dikerjakan = FALSE WHERE id_transaksi = %s"
          await cursor.execute(q2, (data['id_transaksi'], ))

          await conn.commit()
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)

@app.put('/update_menit')
async def update_menit(
  request: Request,
) :
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()
          print(data['sum_durasi_menit'])
          print(data['id_transaksi'])

          q1 = "UPDATE durasi_kerja_sementara SET sum_durasi_menit = %s WHERE id_transaksi = %s"
          await cursor.execute(q1, (data['sum_durasi_menit'], data['id_transaksi']))

          await conn.commit()
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)

@app.delete('/delete_waktu')
async def delete_waktu(
  request: Request,
) :
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()
          print(data['id_transaksi'])

          q1 = "DELETE FROM durasi_kerja_sementara WHERE id_transaksi = %s"
          await cursor.execute(q1, (data['id_transaksi'], ))

          await conn.commit()
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
  
