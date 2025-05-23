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
  prefix="/revisi"
)

@app.get('/transaksi')
async def getLatestTrans(
  id_transaksi: str = Query()
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        q1 = "SELECT * FROM main_transaksi WHERE id_transaksi = %s"
        await cursor.execute(q1, (id_transaksi, ))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')[0]

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  
@app.put('/terapis')
async def updateTerapis(
  request: Request,
  id_transaksi: str = Query(),
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()
          prev_terapis = data['current_terapis']
          new_terapis = data['new_terapis']

          q1 = "UPDATE main_transaksi SET id_terapis = %s, sedang_dikerjakan = 0 WHERE id_transaksi = %s"
          await cursor.execute(q1, (new_terapis, id_transaksi))

          q2 = "UPDATE terapis_kerja SET is_cancel = 1, is_tunda = 0, jam_selesai = NOW() WHERE id_transaksi = %s AND id_terapis = %s"
          await cursor.execute(q2, (id_transaksi, prev_terapis))

          q3 = "UPDATE karyawan SET is_occupied = 0 WHERE id_karyawan = %s"
          await cursor.execute(q3, (prev_terapis, ))

          q4 = "UPDATE karyawan SET is_occupied = 1 WHERE id_karyawan = %s"
          await cursor.execute(q4, (new_terapis, ))

          await conn.commit()

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"Error Mysql": str(e)}, status_code=500)
        
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Error HTTP": str(e.detail)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  
@app.put('/ruangan')
async def updateRuangan(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()
          id_transaksi = data['id_transaksi']
          prev_kode_ruangan = data['prev_kode_ruangan']
          new_kode_ruangan = data['new_kode_ruangan']

          qSelect = "SELECT id_ruangan FROM ruangan WHERE id_karyawan = %s"
          await cursor.execute(qSelect, (new_kode_ruangan, ))
          items = await cursor.fetchone()

          q1 = "UPDATE main_transaksi SET id_ruangan = %s, sedang_dikerjakan = 0 WHERE id_transaksi = %s"
          await cursor.execute(q1, (items[0], id_transaksi))

          q2 = "UPDATE terapis_kerja SET is_tunda = 1 WHERE id_transaksi = %s"
          await cursor.execute(q2, (id_transaksi))

          q3 = "UPDATE ruangan SET status = 'aktif' WHERE id_karyawan = %s"
          await cursor.execute(q3, (prev_kode_ruangan, ))

          q4 = "UPDATE ruangan SET status = 'occupied' WHERE id_karyawan = %s"
          await cursor.execute(q4, (new_kode_ruangan, ))

          q5 = "UPDATE durasi_kerja_sementara SET kode_ruangan = %s WHERE id_transaksi = %s"
          await cursor.execute(q5, (new_kode_ruangan, id_transaksi))

          await conn.commit()
        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"Error Mysql": str(e)}, status_code=500)
        
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Error HTTP": str(e.detail)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)

@app.post('/tambahpaket_produk')
async def addon(
  request: Request,
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()
          id_trans = data['id_transaksi']

          details = data.get('detail_trans', [])
          total_addon = 0
          total_durasi_global = 0
          for item in details:
            new_id_dt = f"DT{uuid.uuid4().hex[:16]}".upper()
            total_addon += item['harga_total']

            if item['satuan'].lower() == "pcs":
              total_durasi = item['jlh'] * item['durasi_awal']
              total_durasi_global += total_durasi

              q2 = """
                INSERT INTO detail_transaksi_produk(
                  id_detail_transaksi, id_transaksi, id_produk, qty, satuan, durasi_awal, 
                  total_durasi, harga_item, harga_total, status, is_addon
                ) 
                VALUES(
                  %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s
                )
              """
              await cursor.execute(q2, 
                (new_id_dt, id_trans, item['id_paket_msg'], item['jlh'], item['satuan'], item['durasi_awal'],
                total_durasi, item['harga_paket_msg'], item['harga_total'], item['status'], item['is_addon'])
              )
            else:
              total_durasi = item['jlh'] * item['durasi_awal']
              total_durasi_global += total_durasi

              q2 = """
                INSERT INTO detail_transaksi_paket(
                  id_detail_transaksi, id_transaksi, id_paket, qty, satuan, durasi_awal, 
                  total_durasi, harga_item, harga_total, status, is_addon
                ) 
                VALUES(
                  %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s
                )
              """
              await cursor.execute(q2, (
                new_id_dt, id_trans, item['id_paket_msg'], item['jlh'], item['satuan'], item['durasi_awal'],
                total_durasi, item['harga_paket_msg'], item['harga_total'], item['status'], item['is_addon']
              ))

          qSelectAddOn = "SELECT total_addon FROM main_transaksi WHERE id_transaksi = %s"
          await cursor.execute(qSelectAddOn, (id_trans, ))
          itemAddOn = await cursor.fetchone()
          currentTotalAddOn = 0 if not itemAddOn[0] else itemAddOn[0]

          q3 = "UPDATE main_transaksi SET total_addon = %s WHERE id_transaksi = %s"
          await cursor.execute(q3, (currentTotalAddOn + total_addon, id_trans))

          # Select Durasi Sementaranya lagi
          q4 = "SELECT sum_durasi_menit FROM durasi_kerja_sementara WHERE id_transaksi = %s"
          await cursor.execute(q4, (id_trans, ))
          items = await cursor.fetchone()
          current_durasi = items[0]
          sum_durasi = current_durasi + total_durasi_global

          q5 = "UPDATE durasi_kerja_sementara SET sum_durasi_menit = %s WHERE id_transaksi = %s"
          await cursor.execute(q5, (sum_durasi, id_trans))

          await conn.commit()

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"Error Mysql": str(e)}, status_code=500)
        
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Error HTTP": str(e.detail)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  

