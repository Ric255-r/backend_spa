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
from jwt_auth import access_security, refresh_security

# Untuk Routingnya jadi http://192.xx.xx.xx:5500/api/fnb/endpointfunction
app = APIRouter(
  prefix="/fnb",
  # dependencies=[Depends(verify_jwt)]
)


# Penggantinya Create Draft Transaksi
# @app.get('/lastId')
# async def getLatestTransaksi():
#   try:
#     pool = await get_db() # Get The pool

#     async with pool.acquire() as conn:  # Auto Release
#       async with conn.cursor() as cursor:

#         q1 = """
#           SELECT id_transaksi FROM main_transaksi 
#           WHERE id_transaksi LIKE 'TF%' 
#           ORDER BY CAST(SUBSTRING(id_transaksi, 3) AS UNSIGNED) DESC
#           LIMIT 1
#           FOR UPDATE
#         """
#         await cursor.execute(q1)

#         items = await cursor.fetchone() #id transaksi terletak di index ke-0
#         id_trans = items[0] if items is not None else None

#         if id_trans is None:
#           num = "1"
#           strpad = "TF" + num.zfill(4)
#         else:
#           getNum = id_trans[2:]
#           num = int(getNum) + 1
#           strpad = "TF" + str(num).zfill(4)

#         return strpad


#   except Exception as e:
#     return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  
@app.post("/createDraft")
async def create_draft_transaksi():
  try:
    pool = await get_db()
    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          q1 = """
            SELECT id_transaksi 
            FROM main_transaksi 
            WHERE id_transaksi LIKE 'TF%' 
            ORDER BY CAST(SUBSTRING(id_transaksi, 3) AS UNSIGNED) DESC
            LIMIT 1
            FOR UPDATE
          """
          await cursor.execute(q1)
          items = await cursor.fetchone()
          last_id = items[0] if items else None

          if last_id:
            getNum = last_id[2:]
            new_num = int(getNum) + 1
          else:
            new_num = 1

          new_id = "TF" + str(new_num).zfill(4)

          # Insert DRAFT entry
          q2 = """
            INSERT INTO main_transaksi (id_transaksi, status)
            VALUES (%s, %s)
          """
          await cursor.execute(q2, (new_id, 'draft'))
          
          await conn.commit()

          return JSONResponse(content={"id_transaksi": new_id}, status_code=200)
        except Exception as e:
          await conn.rollback()
          return JSONResponse(content={"Error Db": str(e)}, status_code=500)


  except Exception as e:

    return JSONResponse(content={"error": str(e)}, status_code=500)
  
@app.delete('/deleteDraftId/{id}')
async def deleteDraftId(
  id: str
) :
  try:
    pool = await get_db()
    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          q1 = """
            DELETE FROM main_transaksi WHERE id_transaksi = %s AND status = %s
          """
          await cursor.execute(q1, (id, 'draft'))
          await conn.commit()

          return JSONResponse(content={"Success": "Delete Draft" }, status_code=200)
        except Exception as e:
          await conn.rollback()
          return JSONResponse(content={"Error Db": str(e)}, status_code=500)


  except Exception as e:

    return JSONResponse(content={"error": str(e)}, status_code=500)


# @app.get('/menu')
# async def getMenu():
#   try:
#     pool = await get_db() # Get The pool

#     async with pool.acquire() as conn:  # Auto Release
#       async with conn.cursor() as cursor:
#         q1 = "SELECT * FROM menu_fnb"
#         await cursor.execute(q1)

#         items = await cursor.fetchall()

#         column_name = []
#         for kol in cursor.description:
#           column_name.append(kol[0])

#         df = pd.DataFrame(items, columns=column_name)
#         return df.to_dict('records')

#   except Exception as e:
#     return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  
@app.post('/store')
async def storeData(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Generate a new id_kategori *inside transaction safely*
          q1 = """
            SELECT id_detail_transaksi FROM detail_transaksi WHERE id_detail_transaksi LIKE 'DT%' 
            ORDER BY id_detail_transaksi DESC LIMIT 1 FOR UPDATE
          """
          await cursor.execute(q1)
          items = await cursor.fetchone()
          id_dt = items[0] if items else None

          if id_dt is None:
              num = 1  # First entry
          else:
              getNum = id_dt[2:]  # Remove 'DT' and get number
              num = int(getNum) + 1

          new_id_dt = "DT" + str(num).zfill(4)

          # 3. Execute query DT
          data = await request.json()

          # Pecah kedalam bentuk list, krna detail_trans bentuk array
          # Query Masukin Ke DetailTrans
          details = data.get('detail_trans', [])
          for item in details:
            q2 = """
              INSERT INTO detail_transaksi(
                id_detail_transaksi, id_fnb, qty, satuan, harga_item, harga_total
              ) 
              VALUES(
                %s, %s, %s, %s, %s, %s
              )
            """
            await cursor.execute(q2, (new_id_dt, item['id_fnb'], item['jlh'], item['satuan'], item['harga_fnb'], item['harga_total']))

          #Query Masukin ke Transaksi
          q3 = """
            UPDATE main_transaksi
            SET
              id_loker = %s, jenis_transaksi = %s, jenis_tamu = %s, id_member = %s, no_hp = %s,
              nama_tamu = %s, id_resepsionis = %s, id_detail_transaksi = %s, total_harga = %s,
              disc = %s, grand_total = %s, metode_pembayaran = %s, 
              jumlah_bayar = %s, jumlah_kembalian = %s, status = %s
            WHERE id_transaksi = %s
          """
          await cursor.execute(q3, (
              2, 'fnb', 'umum', '-', 4141, '-', 'RD001', 
              new_id_dt, data['total_harga'], data['disc'], data['grand_total'],
              True, data['jumlah_bayar'], data['jumlah_bayar'] - data['grand_total'], 'stored',
              data['id_transaksi']  # <- moved to last parameter because it's in WHERE
          ))

        
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
          print(f"Error {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)

