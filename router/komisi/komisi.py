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

        q1 = "SELECT * FROM komisi WHERE id_karyawan = %s AND MONTH(created_at) = %s and YEAR(created_at) = %s ORDER BY id ASC"
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