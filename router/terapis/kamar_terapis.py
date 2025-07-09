from datetime import datetime
import json
from typing import Optional
import uuid
import aiomysql
from fastapi import APIRouter, File, Form, Query, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
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
import traceback
import asyncio

app = APIRouter(
  prefix="/kamar_terapis"
)

kamar_connection = []

@app.websocket("/ws-kamar")
async def kamar_ws(
  websocket: WebSocket
):
  await websocket.accept()
  kamar_connection.append(websocket)
  try:
    # Bikin Koneksi Ttp Nyala
    print("Hai Ws Kamar")
    await websocket.receive_text()

  except WebSocketDisconnect :
    print("ws kamar closed")
    kamar_connection.remove(websocket)

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
  id_trans: Optional[str] = Query(None),
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

          # Start Query Paket. jika id_trans ada isiny, maka ambil data yg sedang_dikerjakan = true
          q_paket = f"""
            SELECT dtpa.id_paket, dtpa.durasi_awal,
            CASE 
              WHEN pm.id_paket_msg IS NOT NULL THEN pm.nama_paket_msg
              WHEN pe.id_paket_extend IS NOT NULL THEN pe.nama_paket_extend
              ELSE 'Unknown Paket'
            END AS nama_paket_msg,  
            dtpa.total_durasi, pm.detail_paket as deskripsi_paket, m.id_transaksi,
            m.created_at as tgl_transaksi, m.id_terapis, dtpa.id_detail_transaksi,
            k.nama_karyawan, r.nama_ruangan, r.id_karyawan AS kode_ruangan, dtpa.status AS status_detail,
            dtpa.is_addon, dtpa.harga_total
            FROM 
              detail_transaksi_paket dtpa 
            INNER JOIN 
              main_transaksi m ON dtpa.id_transaksi = m.id_transaksi
            INNER JOIN 
              karyawan k ON m.id_terapis = k.id_karyawan
            LEFT JOIN 
              ruangan r ON m.id_ruangan = r.id_ruangan
            LEFT JOIN 
              paket_massage pm ON dtpa.id_paket = pm.id_paket_msg
            LEFT JOIN 
              paket_extend pe ON dtpa.id_paket = pe.id_paket_extend
            WHERE 
              m.id_ruangan = %s AND m.sedang_dikerjakan = {'FALSE' if id_trans is None else 'TRUE'}
            AND 
              m.is_cancel = 0
              -- ak tambahin string kosong krn mrk msh gegabah. suka keluar dari aplikasi 
            AND
              m.status NOT IN ('done', 'done-unpaid-addon', 'done-unpaid', 'draft', '')
            AND 
              dtpa.is_returned != 1
            {'AND m.id_transaksi = %s' if id_trans is not None else ''}
            ORDER BY m.created_at DESC
          """ 
          # id karyawan disini adlh id akun yg login. berarti id ruangan.
          if id_trans is not None:
            await cursor.execute(q_paket, (user['id_ruangan'], id_trans))
          else:
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

          # Start Query Produk. jika id_trans ada isiny, maka ambil data yg sedang_dikerjakan = true
          # utk ambil data produk yg udah dibookingnya
          q_produk = f"""
            SELECT dtpa.id_produk, mp.nama_produk, dtpa.durasi_awal, 
            dtpa.total_durasi, m.id_transaksi,
            m.created_at as tgl_transaksi, m.id_terapis, dtpa.id_detail_transaksi, 
            k.nama_karyawan, r.nama_ruangan, r.id_karyawan AS kode_ruangan, dtpa.status AS status_detail,
            dtpa.is_addon
            FROM detail_transaksi_produk dtpa 
            INNER JOIN main_transaksi m ON dtpa.id_transaksi = m.id_transaksi
            INNER JOIN karyawan k ON m.id_terapis = k.id_karyawan
            LEFT JOIN ruangan r ON m.id_ruangan = r.id_ruangan
            LEFT JOIN menu_produk mp ON dtpa.id_produk = mp.id_produk
            WHERE m.id_ruangan = %s AND m.sedang_dikerjakan = {'FALSE' if id_trans is None else 'TRUE'}
            AND 
              m.is_cancel = 0
              -- ak tambahin string kosong krn mrk msh gegabah. suka keluar dari aplikasi 
            AND m.status NOT IN ('done', 'done-unpaid', 'done-unpaid-addon', 'draft', '')
            {'AND m.id_transaksi = %s' if id_trans is not None else ''}
            ORDER BY m.created_at DESC
          """ 
          # id karyawan disini adlh id akun yg login. berarti id ruangan.
          if id_trans is not None:
            await cursor.execute(q_produk, (user['id_ruangan'], id_trans))
          else:
            await cursor.execute(q_produk, (user['id_ruangan'], ))

          column_names = []
          for kol in cursor.description:
            column_names.append(kol[0])

          items2 = await cursor.fetchall()

          print ('isi paket :', items)
          print('isi paket 2:', items2)

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
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
          await conn.begin()
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

          data = await request.json()

          try:
            jam_datang = datetime.strptime(data['jam_datang'], '%H:%M:%S').time()
          except ValueError:
            return JSONResponse(
              content={"status": "error", "message": "Invalid time format, use HH:MM:SS"},
              status_code=400
            )
          
          qCheck = """
            SELECT tk.*, k.nama_karyawan FROM terapis_kerja tk
            INNER JOIN karyawan k ON tk.id_terapis = k.id_karyawan 
            WHERE tk.id_transaksi = %s AND tk.id_terapis = %s AND tk.is_cancel != 1
          """
          await cursor.execute(qCheck, (data['id_transaksi'], data['id_terapis']))
          items = await cursor.fetchone()

          if not items:
            q1 = "INSERT INTO terapis_kerja(id_transaksi, id_terapis, jam_datang) VALUES(%s, %s, %s)"
            await cursor.execute(q1, (data['id_transaksi'], data['id_terapis'], jam_datang))
            await conn.commit()

            # REFETCH after insert
            await cursor.execute(qCheck, (data['id_transaksi'], data['id_terapis']))
            items = await cursor.fetchone()

            if not items:
              raise HTTPException(status_code=500, detail="Failed to retrieve inserted record.")
            # End Refetch

          # Disini Awalnya ku ksh Transaction Isolation. ku pindahkan paling atas          
          q2 = """
            SELECT mt.*, r.nama_ruangan FROM main_transaksi mt
            INNER JOIN ruangan r ON mt.id_ruangan = r.id_ruangan 
            WHERE mt.id_transaksi = %s
            LIMIT 1
          """
          await cursor.execute(q2, (data['id_transaksi'], ))
          items2 = await cursor.fetchone()

          # Ini utk aktifkan websocket kirim ke resepsionis
          for ws_con in kamar_connection:
            await ws_con.send_text(
              json.dumps({
                "id_transaksi": data['id_transaksi'],
                "status": "terapis_tiba",
                "message": f"{items['nama_karyawan']} Telah diruangan {items2['nama_ruangan']}"
              })
            )
          
          print("Isi Item", items)
          print("Isi Item2", items2)
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    error_details = traceback.format_exc()

    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(error_details)}"}, status_code=500)
  

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
  
@app.put('/retur_paket')
async def returPaket(
  request: Request
): 
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
          await conn.begin()

          data = await request.json()
          id_transaksi = data['id_transaksi']
          id_detail_diretur = data['id_detail_diretur']
          alasan_retur = data['alasan_retur']
          # time_spent = data['time_spent']
          # krn bentuk object, pake get
          pengganti = data.get('item_pengganti')
          new_id = f"DT{uuid.uuid4().hex[:16]}".upper()
          table_retur = "detail_transaksi_paket"

          # Query utk tandai item lama yg diretur
          q1 = f"""
            UPDATE {table_retur} SET 
              is_returned = 1, alasan_retur = %s, replaced_by_id_detail = %s, status = 'retur' 
              WHERE id_detail_transaksi = %s
          """
          await cursor.execute(q1, (alasan_retur, new_id, id_detail_diretur))

          # Tambah Item Pengganti
          if pengganti:
            q2 = f"""
              INSERT INTO {table_retur} (
                id_detail_transaksi, id_transaksi, {'id_produk' if table_retur == "detail_transaksi_produk" else 'id_paket'},
                qty, satuan, durasi_awal, 
                total_durasi, harga_item, harga_total, status, is_addon
              ) VALUES (
                %s, %s, %s,
                %s, %s, %s, 
                %s, %s, %s, %s, %s
              )
            """
            id_pengganti = pengganti['id_produk'] if table_retur == "detail_transaksi_produk" else pengganti['id_paket_msg']
            # Default Qty = 1
            qty = 1 if 'qty' not in pengganti else pengganti['qty']
            hrg_total_pengganti = qty * pengganti['harga_paket_msg']
            total_durasi_pengganti = qty * pengganti['durasi']

            await cursor.execute(q2, (
              new_id, id_transaksi, id_pengganti, 
              qty, 'paket', pengganti['durasi'],
              total_durasi_pengganti, pengganti['harga_paket_msg'],
              hrg_total_pengganti, 'unpaid', 0
            ))

          # Bagian Tarik Data Main Transaksi
          qSelectMain = "SELECT * FROM main_transaksi WHERE id_transaksi = %s"
          await cursor.execute(qSelectMain, (id_transaksi, ))
          items = await cursor.fetchone()
          total_hrg_awal = items['total_harga']
          disc_awal = items['disc']
          jumlah_byr_awal = items['jumlah_bayar']
          status_awal = items['status']
          id_ruangan = items['id_ruangan']
          pajak = items['pajak']
          # End Bagian Tarik Data Main

          # Tarik Data yg diretur
          qSelectDetail = "SELECT harga_total, total_durasi FROM detail_transaksi_paket WHERE id_detail_transaksi = %s"
          await cursor.execute(qSelectDetail, (id_detail_diretur, ))
          items2 = await cursor.fetchone()
          harga_retur = items2['harga_total']
          retur_durasi = items2['total_durasi']

          qSelectPaket = "SELECT * FROM paket_massage WHERE id_paket_msg = %s"
          await cursor.execute(qSelectPaket, (id_pengganti, ))
          item_paket = await cursor.fetchone()

          qSelectRuangan = "SELECT nama_ruangan FROM ruangan WHERE id_ruangan = %s"
          await cursor.execute(qSelectRuangan, (id_ruangan, ))
          item_ruangan = await cursor.fetchone()

          # Ini utk aktifkan websocket kirim ke admin
          for ws_con in kamar_connection:
            await ws_con.send_text(
              json.dumps({
                "id_transaksi": id_transaksi,
                "status": "ganti_paket",
                "message": f"Ruangan {item_ruangan['nama_ruangan']} Mengganti Paket ke {item_paket['nama_paket_msg']}"
              })
            )
          # End Tarik data Yg diretur

          # Update main Transaksi
          total_hrg_baru = total_hrg_awal - harga_retur + hrg_total_pengganti
          g_total_baru = 0
          if not disc_awal or disc_awal is None or disc_awal == "" or disc_awal == 0:
            g_total_baru = total_hrg_baru
          else:
            nominal_disc = total_hrg_baru * disc_awal
            g_total_baru = total_hrg_baru - nominal_disc
          
          nominal_pjk = g_total_baru * pajak
          gtotal_stlh_pjk = g_total_baru + nominal_pjk

          q3 = f"""
            UPDATE main_transaksi SET sedang_dikerjakan = 1, total_harga = %s, grand_total = %s, gtotal_stlh_pajak = %s
            {", status = 'unpaid'" if gtotal_stlh_pjk > jumlah_byr_awal else ''}
            WHERE id_transaksi = %s
          """
          await cursor.execute(q3, (total_hrg_baru, g_total_baru, gtotal_stlh_pjk, id_transaksi))
          # End Update Main Transaksi

          # Tarik data lama durasi_kerja_sementara
          qSelectDurasi = "SELECT * FROM durasi_kerja_sementara WHERE id_transaksi = %s"
          await cursor.execute(qSelectDurasi, (id_transaksi, ))
          items3 = await cursor.fetchone()
          durasi_lama = items3['sum_durasi_menit']
          # ubah timespent ke menit
          # menit_kepakai = ()
          formula_durasi = durasi_lama - retur_durasi + total_durasi_pengganti
          # End Tarik durasi_kerja_sementara
          
          q4 = "UPDATE durasi_kerja_sementara SET sum_durasi_menit = %s WHERE id_transaksi = %s"
          await cursor.execute(q4, (formula_durasi, id_transaksi))

          await conn.commit()
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    error_details = traceback.format_exc()
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {error_details}"}, status_code=500)

ob_connections = []

@app.websocket("/ws-ob")
async def spv_ob(
  websocket : WebSocket
) :
  await websocket.accept()
  ob_connections.append(websocket)
  try :
    print('Hai ws ob nyala')
    while True :
      message = await websocket.receive_text()
      print(f"received : {message}")
  except WebSocketDisconnect :
    print("websocket disconnected, removing from list")
    ob_connections.remove(websocket)
  
  except Exception as e :
    print(f"unexpected websocket error : {e}")
    ob_connections.remove(websocket)

async def broadcast_update():
  pool = await get_db()
  async with pool.acquire() as conn:
    async with conn.cursor() as cursor:
      q1 = "SELECT id, nama_ruangan, keterangan FROM kerja_ob_sementara ORDER BY id ASC"
      await cursor.execute(q1)
      result = await cursor.fetchall()

  isidata = [{"id":row[0],"nama_ruangan": row[1], "keterangan" : row[2]} for row in result]

  for websocket in ob_connections:
    await websocket.send_text(
      json.dumps({
        "dataruangan" : isidata})
  ) 
    
@app.put('/selesai')
async def selesai(
  request: Request,
  selesai_awal: Optional[str] = Query(None),
) :
  try: 
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()

          qSelect = f"""
            SELECT id_ruangan, id_terapis, no_loker, total_addon, status FROM main_transaksi 
            WHERE id_transaksi = %s
          """
          await cursor.execute(qSelect, (data['id_transaksi'], ))
          items = await cursor.fetchone()

          id_ruangan = items[0]
          id_terapis = items[1]
          no_loker = items[2]
          total_addon = items[3]
          status = items[4]

          mode = ""
          if total_addon == 0 and status == 'paid':
            mode = 'done'
          elif total_addon != 0 and status == 'paid':
            mode = 'done-unpaid-addon'
          elif total_addon != 0 and status == 'unpaid': 
            mode = 'done-unpaid'
          elif total_addon == 0 and status == 'unpaid':
            mode = 'done-unpaid'
          else:
            if status in ["done", "done-unpaid", "done-unpaid-addon"]:
              mode = status
          
          print("Mode Pas Selesai Kamar", mode)
          q1 = f"""
            UPDATE main_transaksi SET sedang_dikerjakan = FALSE,
            status = '{mode}' WHERE id_transaksi = %s
          """
          await cursor.execute(q1, (data['id_transaksi'], ))

          q2 = f"""
            UPDATE ruangan SET status = 'maintenance' WHERE id_ruangan = %s
          """
          await cursor.execute(q2, (id_ruangan, ))
        
          q3 = f"""
            UPDATE karyawan SET is_occupied = 0 WHERE id_karyawan = %s
          """
          await cursor.execute(q3, (id_terapis, ))

          q4 = f"""
            UPDATE terapis_kerja SET jam_selesai = NOW() 
            {', alasan = %s' if selesai_awal is not None else ''}
            WHERE id_transaksi = %s and id_terapis = %s
          """
          if selesai_awal is not None:
            await cursor.execute(q4, (selesai_awal, data['id_transaksi'], id_terapis))
          else:
            await cursor.execute(q4, (data['id_transaksi'], id_terapis))

          q5 = "DELETE FROM durasi_kerja_sementara WHERE id_transaksi = %s"
          await cursor.execute(q5, (data['id_transaksi'], ))

          q6 = "SELECT nama_ruangan FROM ruangan WHERE id_ruangan = %s"
          await cursor.execute(q6, id_ruangan)

          item6 = await cursor.fetchone()

          namaruangan = item6[0]
          print(namaruangan)

          q7 = "INSERT INTO kerja_ob_sementara (nama_ruangan, keterangan) VALUES (%s,%s) "
          await cursor.execute(q7, (namaruangan, 'Perlu Dibersihkan'))

          await conn.commit() 

          await broadcast_update()

          for ws_con in kamar_connection:
            await ws_con.send_text(
              json.dumps({
                "id_transaksi": data['id_transaksi'],
                "status": "kamar_selesai",
                "message": f"{namaruangan} Telah Selesai digunakan"
              })
            )

          print("Berhasil Eksekusi Semua Fungsi diatas")
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

          q2 = "UPDATE main_transaksi SET sedang_dikerjakan = FALSE, status = 'done' WHERE id_transaksi = %s"
          await cursor.execute(q2, (data['id_transaksi'], ))

          q3 = "SELECT id_ruangan, id_terapis FROM main_transaksi WHERE id_transaksi = %s"
          await cursor.execute(q3, (data['id_transaksi'], ))
          items = await cursor.fetchone()

          id_ruangan = items[0]
          id_terapis = items[1]

          q4 = "UPDATE karyawan SET is_occupied = FALSE WHERE id_karyawan = %s"
          await cursor.execute(q4, (id_terapis, ))

          q5 = "UPDATE ruangan SET status = 'maintenance' WHERE id_ruangan = %s"
          await cursor.execute(q5, (id_ruangan, ))

          await conn.commit()

          return JSONResponse(content={"Status": f"Selesai Transaksi"}, status_code=200)
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
@app.get('/getidmember')
async def getidmember(
  request : Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()
        # await cursor.execute("COMMIT;")

        qtarikmember = "SELECT id_member FROM main_transaksi WHERE id_transaksi = %s"

        await cursor.execute(qtarikmember,(data['id_transaksi']))  

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
@app.put('/panggilob')
async def panggilob(
  request : Request
) :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        qSelect = f"""
            SELECT id_ruangan, id_terapis, no_loker, total_addon, status FROM main_transaksi 
            WHERE id_transaksi = %s
          """
        await cursor.execute(qSelect, (data['id_transaksi'], ))
        items = await cursor.fetchone()

        id_ruangan = items[0]

        q6 = "SELECT nama_ruangan FROM ruangan WHERE id_ruangan = %s"
        await cursor.execute(q6, id_ruangan)

        item6 = await cursor.fetchone()

        namaruangan = item6[0]
        print(namaruangan)

        q7 = "INSERT INTO kerja_ob_sementara (nama_ruangan, keterangan) VALUES (%s, %s) "
        await cursor.execute(q7, (namaruangan, 'Memanggil anda'))

        await conn.commit() 

        await broadcast_update()
        return {"status" : "Panggil OB jalan"}
  except HTTPException as e:
    return JSONResponse({"Error panggil OB": str(e)}, status_code=e.status_code)