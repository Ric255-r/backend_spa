import asyncio
import json
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Query, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
import pandas as pd
from aiomysql import Error as aiomysqlerror
from jwt_auth import access_security, refresh_security, verify_jwt

# Untuk Routingnya jadi http://192.xx.xx.xx:5500/api/fnb/endpointfunction
app = APIRouter(
  prefix="/kitchen",
  # dependencies=[Depends(verify_jwt)]
)


@app.get('/data')
async def dataTrans(
  status: Optional[str] = Query(None)
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        q1 = "SELECT * FROM kitchen WHERE status_pesanan = %s"
        await cursor.execute(q1, (status, ))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  
@app.get('/detailTrans/{id_transaksi}')
async def detailTrans(
  id_transaksi: str,
  status: Optional[str] = Query(None)
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        q1 = """
          SELECT m.id_transaksi, m.id_detail_transaksi, m.id_ruangan, mf.nama_fnb, dt.qty, dt.satuan 
          FROM detail_transaksi dt 
          INNER JOIN main_transaksi m ON m.id_detail_transaksi = dt.id_detail_transaksi
          INNER JOIN menu_fnb mf ON dt.id_fnb = mf.id_fnb
          INNER JOIN kitchen k ON m.id_transaksi = k.id_transaksi
          WHERE m.id_transaksi = %s AND k.status_pesanan = %s
          
        """
        await cursor.execute(q1, (id_transaksi, status))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  
@app.put('/updatePesanan/{id_transaksi}')
async def updatePesanan(
  id_transaksi: str,
  status: Optional[str] = Query(None)
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # ketika status awal process dan mau nge-done, set jam_selesai
          if status == "done":
            q1 = "UPDATE kitchen SET status_pesanan = %s, jam_selesai_psn = CURRENT_TIME() WHERE id_transaksi = %s"
          elif status == "process":
            q1 = "UPDATE kitchen SET status_pesanan = %s, jam_terima_psn = CURRENT_TIME() WHERE id_transaksi = %s"

          await cursor.execute(q1, (status, id_transaksi)) 
          

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
