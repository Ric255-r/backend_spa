import json
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
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
  prefix="/id_trans",
  # dependencies=[Depends(verify_jwt)]
)


# Ini Di Page transaksi_food.dart
@app.post("/createDraft")
async def create_draft_transaksi(
  user: JwtAuthorizationCredentials = Security(access_security)
):
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
            INSERT INTO main_transaksi (id_transaksi, id_resepsionis, status)
            VALUES (%s, %s, %s)
          """
          await cursor.execute(q2, (new_id, user['id_karyawan'], 'draft'))
          
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


@app.put('/updateDraft/{id}')
async def updateDataDraft(
  id: str,
  request: Request
) :
  try:
    pool = await get_db()
    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          await conn.begin()

          data = await request.json()

          
          if "mode" in data and data['mode'] == "for_massage":
            q1 = """
              UPDATE main_transaksi SET no_loker = %s, jenis_tamu = %s, no_hp = %s, nama_tamu = %s,
              id_ruangan = %s, id_terapis = %s, id_gro = %s
              WHERE id_transaksi = %s AND status = 'draft'
            """
            await cursor.execute(q1, (
              data['no_loker'],data['jenis_tamu'], data['no_hp'], data['nama_tamu'],
              data['id_ruangan'], data['id_terapis'], data['id_gro'], id
            ))
          else:
            q1 = """
              UPDATE main_transaksi SET jenis_tamu = %s, no_hp = %s, nama_tamu = %s WHERE id_transaksi = %s AND status = 'draft'
            """
            await cursor.execute(q1, (data['jenis_tamu'], data['no_hp'], data['nama_tamu'], id))
          
          await conn.commit()

          return JSONResponse(content={"Success": "Update Draft" }, status_code=200)
        except Exception as e:
          await conn.rollback()
          return JSONResponse(content={"Error Db": str(e)}, status_code=500)


  except Exception as e:

    return JSONResponse(content={"error": str(e)}, status_code=500)
# End Transaksi_food.dart