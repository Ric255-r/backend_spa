import asyncio
import json
import os
from typing import Optional
import uuid
import aiomysql
from fastapi import APIRouter, Query, Depends, File, Form, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
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
import calendar
import time
import numpy as np
# Untuk Routingnya jadi http://192.xx.xx.xx:5500/api/fnb/endpointfunction
app = APIRouter(
  prefix="/history",
  # dependencies=[Depends(verify_jwt)]
)

@app.get('/historymember/{id_member}')
async def getHistory(id_member: str):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

                q1 = """
                SELECT
                    dtm.kode_promo,
                    p.nama_promo,
                    pm.id_paket_msg,
                    pm.nama_paket_msg,
                    dpk.detail_kode_promo AS dpk_kode,
                    dpt.detail_kode_promo AS dpt_kode,
                    dtm.sisa_kunjungan,
                    dtm.exp_kunjungan,
                    dtm.exp_tahunan
                FROM
                    detail_transaksi_member dtm
                JOIN
                    promo p ON dtm.kode_promo = p.kode_promo
                LEFT JOIN
                    detail_promo_kunjungan dpk ON dpk.detail_kode_promo = p.detail_kode_promo
                LEFT JOIN
                    detail_promo_tahunan dpt ON dpt.detail_kode_promo = p.detail_kode_promo
                LEFT JOIN
                    paket_massage pm ON p.nama_promo = pm.nama_paket_msg
                WHERE
                    dtm.id_member = %s
                    AND (
                        (dtm.sisa_kunjungan > 0 AND (dtm.exp_kunjungan >= CURDATE() OR dtm.exp_tahunan >= CURDATE()))
                        OR
                        (dtm.sisa_kunjungan IS NULL AND dtm.exp_tahunan >= CURDATE())
                    )
                """
                await cursor.execute(q1, (id_member,))
                items = await cursor.fetchall()

                column_name = [col[0] for col in cursor.description]
                df = pd.DataFrame(items, columns=column_name)

                df = df.replace({np.nan: "", None: ""})  # Replace NaN/None with empty string

                # Convert every value to string, removing `.0` from whole-number floats
                for col in df.columns:
                    df[col] = df[col].map(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x))


                # Then convert to list of dicts
                result = df.to_dict(orient="records")

                # Apply logic: set harga to 0 for kunjungan promo with remaining visits
                for row in result:
                    is_kunjungan_promo = str(row.get('detail_kode_promo', '')).startswith('DK')
                    sisa_kunjungan_str = row.get('sisa_kunjungan', '0')
                    
                    try:
                        sisa_kunjungan = int(sisa_kunjungan_str) if sisa_kunjungan_str.strip().isdigit() else 0
                    except:
                        sisa_kunjungan = 0

                    if is_kunjungan_promo and sisa_kunjungan > 0:
                        row['harga'] = "0"

                return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get('/historymemberkunjungan/{id_member}')
async def getHistory(id_member: str):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

                q1 = """
                SELECT
                dtm.kode_promo,
                p.nama_promo,
                pm.id_paket_msg,
                pm.nama_paket_msg,
                dpk.detail_kode_promo AS dpk_kode,
                dtm.sisa_kunjungan,
                dtm.exp_kunjungan
            FROM
                detail_transaksi_member dtm
            JOIN
                promo p ON dtm.kode_promo = p.kode_promo
            LEFT JOIN
                detail_promo_kunjungan dpk ON dpk.detail_kode_promo = p.detail_kode_promo
            LEFT JOIN
                paket_massage pm ON p.nama_promo = pm.nama_paket_msg
            WHERE
                dtm.id_member = %s
                AND dpk.detail_kode_promo IS NOT NULL
                AND dtm.sisa_kunjungan > 0
                AND dtm.exp_kunjungan >= CURDATE()
                """
                await cursor.execute(q1, (id_member,))
                items = await cursor.fetchall()

                column_name = [col[0] for col in cursor.description]
                df = pd.DataFrame(items, columns=column_name)

                df = df.replace({np.nan: "", None: ""})  # Replace NaN/None with empty string

                # Convert every value to string, removing `.0` from whole-number floats
                for col in df.columns:
                    df[col] = df[col].map(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x))


                # Then convert to list of dicts
                result = df.to_dict(orient="records")

                # Apply logic: set harga to 0 for kunjungan promo with remaining visits
                for row in result:
                    is_kunjungan_promo = str(row.get('detail_kode_promo', '')).startswith('DK')
                    sisa_kunjungan_str = row.get('sisa_kunjungan', '0')
                    
                    try:
                        sisa_kunjungan = int(sisa_kunjungan_str) if sisa_kunjungan_str.strip().isdigit() else 0
                    except:
                        sisa_kunjungan = 0

                    if is_kunjungan_promo and sisa_kunjungan > 0:
                        row['harga'] = "0"

                return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/detail_member/{id_member}")
async def get_member_detail(id_member: str):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "SELECT id_gelang FROM member WHERE id_member = %s"
                await cursor.execute(query, (id_member,))
                result = await cursor.fetchone()

                if result is None:
                    raise HTTPException(status_code=404, detail="Member not found")

                id_gelang = result[0]

                # Build full URL (adjust the base URL as needed)
                qr_filename = os.path.basename(id_gelang)
                base_url = "http://0.0.0.0:5500"  # Change this to your IP or domain
                qr_url = f"{base_url}/qrcodes/{qr_filename}"

                return JSONResponse(status_code=200, content={
                    "status": "Success",
                    "qr_url": qr_url
                })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "Error",
            "message": str(e)
        })