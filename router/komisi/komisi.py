from typing import Optional
import uuid
import aiomysql
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
  prefix="/cekkomisi",
)

@app.get('/listkomisi')
async def getlistkomisi(request : Request):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT * FROM komisi WHERE id_karyawan = %s AND MONTH(created_at) = %s and YEAR(created_at) = %s AND nominal_komisi != 0 ORDER BY id ASC"
        await cursor.execute(q1, (data['id_user'], data['month'], data['year']))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)
  
@app.get('/listkomisimonthly')
async def getlistkomisi(request : Request):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT YEAR(created_at) AS year, MONTH(created_at) AS month, sum(nominal_komisi) AS total_komisi FROM komisi WHERE id_karyawan = %s AND YEAR(created_at) = %s GROUP BY YEAR(created_at), MONTH(created_at) ORDER BY YEAR(created_at) DESC, MONTH(created_at) ASC"
        await cursor.execute(q1, (data['id_user'], data['year']))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)

@app.get('/detailpaket')
async def detailpaket(request : Request):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT * FROM komisi WHERE id_karyawan = %s AND MONTH(created_at) = %s and YEAR(created_at) = %s AND id = %s ORDER BY id ASC"
        await cursor.execute(q1, (data['id_user'], data['month'], data['year'], data['id']))

        items = await cursor.fetchall()
        idtranskomisi = items[0]['id_transaksi']

        q2 = "SELECT id_paket AS id_paket, qty as qty, harga_total as harga_total , is_addon as addon FROM detail_transaksi_paket WHERE id_transaksi = %s "
        await cursor.execute(q2, (idtranskomisi))

        itempaket = await cursor.fetchall()

        all_data =[]

        for item in itempaket :
          idpaket = item['id_paket']
          
          if idpaket[0] == 'M' : 
            q3 = "SELECT nama_paket_msg ,tipe_komisi, nominal_komisi, tipe_komisi_gro, nominal_komisi_gro FROM paket_massage WHERE id_paket_msg = %s "
            await cursor.execute(q3, (idpaket))
            datakomisi = await cursor.fetchone()
          else :
            q4 = "SELECT nama_paket_extend, nominal_komisi FROM paket_extend WHERE id_paket_extend = %s"
            await cursor.execute(q4, (idpaket))
            isiq4 = await cursor.fetchone()
            datakomisi = {
              "nama_paket_msg" : isiq4['nama_paket_extend'],
              "tipe_komisi": 1,
              "nominal_komisi": isiq4['nominal_komisi'],
              "tipe_komisi_gro": 1,
              "nominal_komisi_gro": 0
              }
          combined_data = {
          **item, **datakomisi
            }
          
          all_data.append(combined_data)
          
        return JSONResponse({"data_transaksi" : all_data}) 

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)
  
@app.get('/detailproduk')
async def detailproduk(request : Request):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor(aiomysql.DictCursor) as cursor:  
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT * FROM komisi WHERE id_karyawan = %s AND MONTH(created_at) = %s and YEAR(created_at) = %s AND id = %s ORDER BY id ASC"
        await cursor.execute(q1, (data['id_user'], data['month'], data['year'], data['id']))

        items = await cursor.fetchall()
        idtranskomisi = items[0]['id_transaksi']

        q2 = "SELECT id_produk AS id_paket, qty as qty, harga_total as harga_total , is_addon as addon FROM detail_transaksi_produk WHERE id_transaksi = %s "
        await cursor.execute(q2, (idtranskomisi))

        itempaket = await cursor.fetchall()

        all_data =[]

        for item in itempaket :
          idpaket = item['id_paket']
          
          q3 = "SELECT nama_produk ,tipe_komisi, nominal_komisi, tipe_komisi_gro, nominal_komisi_gro FROM menu_produk WHERE id_produk = %s "
          await cursor.execute(q3, (idpaket))
          datakomisi = await cursor.fetchone()
         
          combined_data = {
          **item, **datakomisi
            }
          
          all_data.append(combined_data)
        
        return JSONResponse({"data_transaksi" : all_data}) 

  except Exception as e:
    return JSONResponse({"Error Get Data Ruangan": str(e)}, status_code=500)
  

@app.get('/listkomisiowner')
async def getlistkomisi(request : Request):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT id_karyawan, SUM(nominal_komisi) AS total_komisi FROM komisi WHERE nominal_komisi != 0 AND MONTH(created_at) = %s and YEAR(created_at) = %s GROUP BY id_karyawan ORDER BY id_karyawan DESC"
        await cursor.execute(q1, (data['month'], data['year']))
        items = await cursor.fetchall()

        result = []
        for row in items:
          id_karyawan = row[0]
          q2 = "SELECT nama_karyawan FROM karyawan where id_karyawan = %s"
          await cursor.execute(q2, id_karyawan)
          nama = await cursor.fetchone()
          result.append({
            "id_karyawan": id_karyawan,
            "nama_karyawan": nama[0],
            "total_komisi":  row[1]
          })
        
        print(result)
        return result

  except Exception as e:
    return JSONResponse({"Error Get Data Komisi": str(e)}, status_code=500)

@app.get('/listkomisiownertahunan')
async def getlistkomisi(request : Request):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT id_karyawan, SUM(nominal_komisi) AS total_komisi FROM komisi WHERE nominal_komisi != 0 AND YEAR(created_at) = %s GROUP BY id_karyawan ORDER BY id_karyawan DESC"
        await cursor.execute(q1, (data['year']))
        items = await cursor.fetchall()

        result = []
        for row in items:
          id_karyawan = row[0]
          q2 = "SELECT nama_karyawan FROM karyawan where id_karyawan = %s"
          await cursor.execute(q2, id_karyawan)
          nama = await cursor.fetchone()
          result.append({
            "id_karyawan": id_karyawan,
            "nama_karyawan": nama[0],
            "total_komisi":  row[1]
          })
        
        print(result)
        return result

  except Exception as e:
    return JSONResponse({"Error Get Data Komisi": str(e)}, status_code=500)
  

@app.get('/listkomisiownerharian')
async def getlistkomisi(request : Request):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        data = await request.json()

        q1 = "SELECT id_karyawan, SUM(nominal_komisi) AS total_komisi FROM komisi WHERE nominal_komisi != 0 AND DATE(created_at) BETWEEN %s AND %s GROUP BY id_karyawan ORDER BY id_karyawan DESC"
        await cursor.execute(q1, (data['startdate'], data['enddate']))
        items = await cursor.fetchall()

        result = []
        for row in items:
          id_karyawan = row[0]
          q2 = "SELECT nama_karyawan FROM karyawan where id_karyawan = %s"
          await cursor.execute(q2, id_karyawan)
          nama = await cursor.fetchone()
          result.append({
            "id_karyawan": id_karyawan,
            "nama_karyawan": nama[0],
            "total_komisi":  row[1]
          })
        
        print(result)
        return result

  except Exception as e:
    return JSONResponse({"Error Get Data Komisi": str(e)}, status_code=500)