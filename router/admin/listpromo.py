from typing import Optional
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror
from datetime import datetime
import asyncio

app = APIRouter(prefix=("/listpromo"))

@app.get('/getdatapromohappyhour')
async def getdatapromohappyhour() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")
        q1 = """
            SELECT 
            a.kode_promo, 
            a.nama_promo, 
            b.detail_kode_promo, 
            b.senin, b.selasa, b.rabu, b.kamis, b.jumat, b.sabtu, b.minggu,
            TIME_FORMAT(b.jam_mulai, '%H:%i') AS jam_mulai, 
            TIME_FORMAT(b.jam_selesai, '%H:%i') AS jam_selesai, 
            b.disc,
            b.umum, 
            b.member, 
            b.vip 
          FROM promo a 
          INNER JOIN detail_promo_happyhour b 
            ON a.detail_kode_promo = b.detail_kode_promo 
          
          ORDER BY a.kode_promo ASC
            """
        await cursor.execute(q1)  

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)
  
@app.get('/getdatapromohappyhourdisc')
async def getdatapromohappyhourdisc(statusTamu: str = None):
    try:
        pool = await get_db()

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

                # Determine filter based on statusTamu
                filter_by_status = ""
                if statusTamu == "Umum":
                    filter_by_status = "AND b.umum = 1"
                elif statusTamu == "Member":
                    filter_by_status = "AND b.member = 1"
                elif statusTamu == "VIP":
                    filter_by_status = "AND b.vip = 1"

                q1 = f"""
                    SELECT 
                      a.kode_promo, 
                      a.nama_promo, 
                      b.detail_kode_promo, 
                      b.senin, b.selasa, b.rabu, b.kamis, b.jumat, b.sabtu, b.minggu,
                      TIME_FORMAT(b.jam_mulai, '%H:%i') AS jam_mulai, 
                      TIME_FORMAT(b.jam_selesai, '%H:%i') AS jam_selesai, 
                      b.disc, 
                      b.umum,
                      b.member, 
                      b.vip 
                    FROM promo a 
                    INNER JOIN detail_promo_happyhour b 
                      ON a.detail_kode_promo = b.detail_kode_promo 
                    WHERE 
                      CURTIME() BETWEEN b.jam_mulai AND b.jam_selesai
                      AND CASE DAYOFWEEK(CURDATE())
                        WHEN 1 THEN b.minggu
                        WHEN 2 THEN b.senin
                        WHEN 3 THEN b.selasa
                        WHEN 4 THEN b.rabu
                        WHEN 5 THEN b.kamis
                        WHEN 6 THEN b.jumat
                        WHEN 7 THEN b.sabtu
                      END = 1
                      {filter_by_status}
                    ORDER BY a.kode_promo ASC
                """

                await cursor.execute(q1)

                items = await cursor.fetchall()
                kolom_menu = [kolom[0] for kolom in cursor.description]
                df = pd.DataFrame(items, columns=kolom_menu)

                return df.to_dict('records')

    except HTTPException as e:
        return JSONResponse({"Error": str(e)}, status_code=e.status_code)



@app.put('/updatepromohappyhour')
async def updatepromohappyhour(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Execute querynya
          data = await request.json()
          q1 = "UPDATE promo SET nama_promo = %s, updated_at =%s WHERE kode_promo = %s"
          await cursor.execute(q1, (data['nama_promo'], datetime.now(),data['kode_promo']))
          q2 = "UPDATE detail_promo_happyhour SET senin = %s, selasa = %s, rabu = %s, kamis = %s, jumat = %s, sabtu = %s, minggu = %s,disc = %s, jam_mulai = %s, jam_selesai = %s, umum = %s, member = %s, vip = %s, updated_at = %s WHERE detail_kode_promo = %s"
          await cursor.execute(q2, (int(data['senin']),int(data['selasa']),int(data['rabu']),int(data['kamis']),int(data['jumat']),int(data['sabtu']),int(data['minggu']),data['disc'],data['jam_mulai'],data['jam_selesai'],data['umum'],data['member'],data['vip'],datetime.now(),data['detail_kode_promo']))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "succes"
        except aiomysqlerror.MySQLError as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error during insert : {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
@app.delete('/deletepromohappyhour')
async def deletepromohappyhour(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Execute querynya
          data = await request.json()
          q1 = "DELETE FROM detail_promo_happyhour WHERE detail_kode_promo IN(SELECT kode_detail_promo FROM PROMO  WHERE kode_promo = %s)"
          await cursor.execute(q1, (data['kode_promo']))

          q2 = "DELETE FROM PROMO WHERE kode_promo = %s"
          await cursor.execute(q2,(data['kode_promo']))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "succes"
        except aiomysqlerror.MySQLError as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error during insert : {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)



@app.get('/getdatapromokunjungan')
async def getdatapromokunjungan() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = """
            SELECT a.kode_promo, a.nama_promo, 
            b.detail_kode_promo, b.limit_kunjungan, b.harga_satuan, b.harga_promo, b.durasi, b.discount, b.limit_promo, c.nama_paket_msg, c.harga_paket_msg
            FROM promo a 
            INNER JOIN detail_promo_kunjungan b 
            ON a.detail_kode_promo = b.detail_kode_promo
            INNER JOIN paket_massage c
            ON a.nama_promo = c.nama_paket_msg
            ORDER BY a.kode_promo ASC;
            """
        await cursor.execute(q1)  

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)


@app.put('/updatepromokunjungan')
async def updatepromokunjungan(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Execute querynya
          data = await request.json()
          q1 = "UPDATE promo SET nama_promo = %s , updated_at = %s WHERE kode_promo = %s"
          await cursor.execute(q1,data['nama_promo'],datetime.now(),data['kode_promo'])
          q2 = "UPDATE detail_promo_kunjungan SET limit_kunjungan = %s, limit_promo = %s, harga_promo = %s, discount = %s, updated_at = %s WHERE detail_kode_promo = %s"
          await cursor.execute(q2, (data['limit_kunjungan'],data['limit_promo'],data['harga_promo'],data['discount'],datetime.now(),data['detail_kode_promo']))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "succes"
        except aiomysqlerror.MySQLError as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error during insert : {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
@app.delete('/deletepromokunjungan')
async def deletepromokunjungan(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Execute querynya
          data = await request.json()
          q1 = "DELETE FROM detail_promo_kunjungan WHERE detail_kode_promo IN(SELECT detail_kode_promo FROM PROMO  WHERE kode_promo = %s)"
          await cursor.execute(q1, (data['kode_promo']),)

          q2 = "DELETE FROM PROMO WHERE kode_promo = %s"
          await cursor.execute(q2,(data['kode_promo']),)
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "succes"
        except aiomysqlerror.MySQLError as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error during insert : {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)


@app.get('/getdatapromotahunan')
async def getdatapromotahunan() :
  try :
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # await cursor.execute("COMMIT;")

        q1 = """
            SELECT a.kode_promo, a.nama_promo, 
            b.detail_kode_promo, b.jangka_tahun, b.harga_promo
            FROM promo a 
            INNER JOIN detail_promo_tahunan b 
            ON a.detail_kode_promo = b.detail_kode_promo 
            ORDER BY a.kode_promo ASC;
            """
        await cursor.execute(q1)  

        items = await cursor.fetchall()

        kolom_menu = [kolom[0] for kolom in cursor.description]
        df = pd.DataFrame(items, columns=kolom_menu)

        # print(" Final fetched items:", items)
        return df.to_dict('records')
  except HTTPException as e:
   return JSONResponse({"Error": str(e)}, status_code=e.status_code)


@app.put('/updatepromotahunan')
async def updatepromotahunan(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Execute querynya
          data = await request.json()
          q1 = "UPDATE promo SET nama_promo = %s , updated_at = %s WHERE kode_promo = %s"
          await cursor.execute(q1, (data['nama_promo'],datetime.now(),data['kode_promo']))
          q2 = "UPDATE detail_promo_tahunan SET jangka_tahun = %s, harga_promo = %s, updated_at = %s WHERE detail_kode_promo = %s"
          await cursor.execute(q2, (data['jangka_tahun'],data['harga_promo'],datetime.now(),data['detail_kode_promo']))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "succes"
        except aiomysqlerror.MySQLError as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error during insert : {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
@app.delete('/deletepromotahunan')
async def deletepromotahunan(
  request: Request
):
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          # 2. Execute querynya
          data = await request.json()
          q1 = "DELETE FROM detail_promo_tahunan WHERE detail_kode_promo IN(SELECT detail_kode_promo FROM PROMO  WHERE kode_promo = %s)"
          await cursor.execute(q1, (data['kode_promo']))

          q2 = "DELETE FROM PROMO WHERE kode_promo = %s"
          await cursor.execute(q2,(data['kode_promo']))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "succes"
        except aiomysqlerror.MySQLError as e:
          # Rollback Input Jika Error

          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error during insert : {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)