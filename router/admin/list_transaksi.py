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

app = APIRouter(
  prefix="/listtrans",
)

@app.get('/datatrans')
async def getDataTrans():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT mt.*, COALESCE(r.nama_ruangan, '-') AS nama_ruangan FROM main_transaksi mt LEFT JOIN ruangan r ON mt.id_ruangan = r.id_ruangan ORDER BY mt.id_transaksi ASC"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)

@app.get('/detailtrans')
async def getDataDetailTrans():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = """SELECT 
            dt.id_detail_transaksi,
            GROUP_CONCAT(DISTINCT mt.id_produk) AS produk_list,
            GROUP_CONCAT(DISTINCT mt.id_fnb) AS fnb_list,
            GROUP_CONCAT(DISTINCT mt.id_paket) AS paket_list,
  
            GROUP_CONCAT(DISTINCT dtp.id_produk) AS produk_list_detail,
            GROUP_CONCAT(DISTINCT dtp.qty) AS produk_qty_list,
            GROUP_CONCAT(DISTINCT dtp.satuan) AS produk_satuan_list,
            GROUP_CONCAT(DISTINCT dtp.harga_item) AS produk_harga_item_list,
            GROUP_CONCAT(DISTINCT dtp.harga_total) AS produk_harga_total_list,

            GROUP_CONCAT(DISTINCT dtpk.id_paket) AS paket_list_detail,
            GROUP_CONCAT(DISTINCT dtpk.qty) AS paket_qty_list,
            GROUP_CONCAT(DISTINCT dtpk.satuan) AS paket_satuan_list,
            GROUP_CONCAT(DISTINCT dtpk.durasi_awal) AS paket_durasi_awal_list,
            GROUP_CONCAT(DISTINCT dtpk.total_durasi) AS paket_total_durasi_list,
            GROUP_CONCAT(DISTINCT dtpk.harga_item) AS paket_harga_item_list,
            GROUP_CONCAT(DISTINCT dtpk.harga_total) AS paket_harga_total_list

            FROM detail_transaksi dt
            LEFT JOIN main_transaksi mt ON dt.id_detail_transaksi = mt.id_detail_transaksi
            LEFT JOIN detail_transaksi_produk dtp ON dt.id_detail_transaksi = dtp.id_detail_transaksi
            LEFT JOIN detail_transaksi_paket dtpk ON dt.id_detail_transaksi = dtpk.id_detail_transaksi
            GROUP BY dt.id_detail_transaksi"""
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)





# @app.get('/detailtrans')
# async def getDataDetailTrans():
#   try:
#     pool = await get_db() # Get The pool

#     async with pool.acquire() as conn:  # Auto Release
#       async with conn.cursor() as cursor:
#         await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
#         q1 = "SELECT dt.*, mt.* FROM detail_transaksi dt LEFT JOIN main_transaksi mt ON dt.id_detail_transaksi = mt.id_detail_transaksi ORDER BY dt.id_detail_transaksi ASC"
#         await cursor.execute(q1)
#         q2 = "SELECT dt.*, mt.* FROM detail_transaksi_paket dt LEFT JOIN main_transaksi mt ON dt.id_detail_transaksi = mt.id_detail_transaksi ORDER BY dt.id_detail_transaksi ASC"
#         await cursor.execute(q2)
#         q3 = "SELECT dt.*, mt.* FROM detail_transaksi_produk dt LEFT JOIN main_transaksi mt ON dt.id_detail_transaksi = mt.id_detail_transaksi ORDER BY dt.id_detail_transaksi ASC"
#         await cursor.execute(q3)

#         items = await cursor.fetchall()

#         column_name = []
#         for kol in cursor.description:
#           column_name.append(kol[0])

#         df = pd.DataFrame(items, columns=column_name)
#         return df.to_dict('records')

#   except Exception as e:
#     return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)