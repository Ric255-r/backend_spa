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

@app.get('/lastId')
async def getLatestTransaksi():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_transaksi FROM main_transaksi WHERE id_transaksi LIKE 'TF%' ORDER BY id_transaksi DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_trans = items[0] if items is not None else None

        if id_trans is None:
          num = "1"
          strpad = "TF" + num.zfill(4)
        else:
          getNum = id_trans[2:]
          num = int(getNum) + 1
          strpad = "TF" + str(num).zfill(4)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  

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
  
  
