from typing import Optional

import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror

app = APIRouter(prefix=("/produk"))

async def getlastestidproduk():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:

        q1 = "SELECT id_produk FROM menu_produk WHERE id_produk LIKE 'P%' ORDER BY id_produk DESC"
        await cursor.execute(q1)

        items = await cursor.fetchone() #id transaksi terletak di index ke-0
        id_produk = items[0] if items is not None else None

        if id_produk is None:
          num = "1"
          strpad = "P" + num.zfill(3)
        else:
          getNum = id_produk[1:]
          num = int(getNum) + 1
          strpad = "P" + str(num).zfill(3)

        return strpad


  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)
  

@app.post('/daftarproduk')
async def postpaket(request: Request):
    try:
        pool = await get_db()

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await conn.begin()
                    lastidproduk = await getlastestidproduk()

                    data = await request.json()

                    # Use .get() with default values
                    nama_produk = data.get("nama_produk")
                    harga_produk = data.get("harga_produk", 0)
                    stok_produk = data.get("stok_produk", 0)
                    durasi = data.get("durasi", 0)
                    tipe_komisi = data.get("tipe_komisi", 0)
                    nominal_komisi = data.get("nominal_komisi", 0)
                    tipe_komisi_gro = data.get("tipe_komisi_gro", 0)
                    nominal_komisi_gro = data.get("nominal_komisi_gro", 0)

                    q1 = """
                        INSERT INTO menu_produk(
                            id_produk, nama_produk, harga_produk, stok_produk, durasi,
                            tipe_komisi, nominal_komisi, tipe_komisi_gro, nominal_komisi_gro
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(q1, (
                        lastidproduk, nama_produk, harga_produk, stok_produk, durasi,
                        tipe_komisi, nominal_komisi, tipe_komisi_gro, nominal_komisi_gro
                    ))

                    await conn.commit()
                    return "Success"

                except aiomysqlerror as e:
                    await conn.rollback()
                    error_code = e.args[0] if e.args else "Unknown"
                    return JSONResponse(
                        content={"status": "Error", "message": f"Database Error {e}"},
                        status_code=500
                    )

                except Exception as e:
                    await conn.rollback()
                    return JSONResponse(
                        content={"status": "Error", "message": f"Server Error {e}"},
                        status_code=500
                    )

    except Exception as e:
        return JSONResponse(
            content={"status": "Error", "message": f"Koneksi Error {str(e)}"},
            status_code=500
        )


@app.get('/getnamaproduk')
async def getnamaproduk() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = "SELECT nama_produk FROM menu_produk ORDER BY id_produk DESC"

        await cursor.execute(q1)

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  

@app.get('/getnamaproduk')
async def getnamaproduk() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = "SELECT nama_produk FROM menu_produk ORDER BY id_produk DESC"

        await cursor.execute(q1)

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)