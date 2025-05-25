from typing import Optional

import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror

app = APIRouter(prefix=("/massage"))

async def getlatestidpaketmassage():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_paket_msg FROM paket_massage WHERE id_paket_msg LIKE 'M%' ORDER BY id_paket_msg DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_category = items[0] if items is not None else None

        if id_category is None:
          num = "1"
          strpad = "M" + num.zfill(3)
        else:
          getNum = id_category[1:]
          num = int(getNum) + 1
          strpad = "M" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  
  
@app.post('/daftarpaketmassage')
async def postpaketmassage(
  request : Request
) :
  try:
    pool = await get_db()
    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()
          lastidpaketmsg = await getlatestidpaketmassage()

          # 2. Execute querynya
          data = await request.json()
          q1 = "INSERT INTO paket_massage(id_paket_msg,nama_paket_msg,harga_paket_msg,durasi,nominal_komisi,tipe_komisi,tipe_komisi_gro,nominal_komisi_gro,detail_paket) VALUES(%s, %s, %s, %s, %s, %s, %s,%s,%s)"
          await cursor.execute(q1, (lastidpaketmsg,data['nama_paket_msg'], data['harga_paket_msg'], data['durasi'],data['nominal_komisi'],data['tipe_komisi'],data['tipe_komisi_gro'],data['nominal_komisi_gro'],data['detail_paket']))

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "Succes"
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
  
@app.get('/getnamapaketmassage')
async def getnamapaketmassage() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = "SELECT nama_paket_msg FROM paket_massage ORDER BY id_paket_msg DESC"

        await cursor.execute(q1)

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)