import json
import traceback
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Query, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from fastapi.staticfiles import StaticFiles
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
import pandas as pd
from aiomysql import Error as aiomysqlerror
from jwt_auth import access_security, refresh_security
import os
import asyncio

IMAGEDIR = "assets/ob"
if not os.path.exists(IMAGEDIR):
    os.makedirs(IMAGEDIR)

app = APIRouter(
  prefix="/ob",
  # dependencies=[Depends(verify_jwt)]
)


@app.get('/list_room')
async def getMenu():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        q1 = "SELECT * FROM ruangan"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Ruangan endpoint /list_room ": str(e)}, status_code=500)
  
# Alurnya harus darisini dlu, baru tarik data
@app.post('/store_waktu')
async def storeWaktu(
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
          q1 = "INSERT INTO laporan_ob(id_ruangan, id_karyawan, jam_mulai) VALUES(%s, %s, %s)"
          await cursor.execute(q1, (data['id_ruangan'], data['id_karyawan'], data['jam_mulai'], ))

          # Ambil Id Yg Udah di Insert
          await cursor.execute("SELECT LAST_INSERT_ID()")
          last_id = await cursor.fetchone()

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          print(last_id)

          return {
            "status": "Success",
            "message": "Data successfully stored",
            "last_id": last_id[0]  # Get the first element of the result (the ID)
          }

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
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)

@app.put('/done_bekerja')
async def doneKerja(
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
          q1 = """
            UPDATE laporan_ob SET jam_selesai = %s, updated_at = CURRENT_TIME() WHERE id_laporan = %s AND id_karyawan = %s
          """
          await cursor.execute(q1, (data['jam_selesai'], data['id_laporan'], data['id_karyawan'], ))

          q2 = """
            UPDATE ruangan SET status = %s WHERE id_ruangan = %s

          """
          await cursor.execute(q2, (data['status'], data['id_ruangan'],))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "Sukses Update Data"
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
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  

@app.put('/update_laporan')
async def updateLaporan(
  request: Request,
  files: List[UploadFile] = File(...)
):
  try:
    pool = await get_db()
    saved_files = []

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # Ensure directory exists
          if not os.path.exists(IMAGEDIR):
            os.makedirs(IMAGEDIR)

          data = await request.form()
          id_laporan = int(data.get('id_laporan'))
          id_karyawan = data.get('id_karyawan')

          # Cek dulu Datanya Exists Atau Ngga.
          await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

          q1 = "SELECT foto_laporan FROM laporan_ob WHERE id_laporan = %s AND id_karyawan = %s LIMIT 1"
          await cursor.execute(q1, (id_laporan, id_karyawan))
          result = await cursor.fetchone()

          # Delete Image Klo ada data
          if result and result[0]:
            try:
              exists_file = json.loads(result[0])
              print(exists_file)
              for filename in exists_file:
                file_path = os.path.join(IMAGEDIR, filename)
                if os.path.exists(file_path):
                  os.remove(file_path)
                  print("Deleted Old File")
            except (json.JSONDecodeError, TypeError) as e:
              print(f"Error Parsing File {e}")
          # End Bagian Delete

          # Ksh Delay Dikit 
          await asyncio.sleep(0.2)

          #  1. Start Transaction
          await conn.begin()

          if files:
            # Create a unique filename
            for file in files:
              filename = f"{uuid.uuid4()}.jpg"
              file_location = os.path.join(IMAGEDIR, filename)

              # Read and save the file
              content = await file.read()
              with open(file_location, "wb") as f:
                f.write(content)
              
              saved_files.append(filename)

          # In your database update section:
          if saved_files:
            # Convert list to JSON string
            foto_laporan_str = json.dumps(saved_files)
          else:
            foto_laporan_str = None  # or '[]' if you prefer empty array representation

          q1 = """
            UPDATE laporan_ob SET foto_laporan = %s, laporan = %s WHERE id_laporan = %s AND id_karyawan = %s
          """
          await cursor.execute(q1, (foto_laporan_str, data.get('laporan'), id_laporan, id_karyawan, ))

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "Sukses Update Data"
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
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  

@app.delete('/delete_progress')
async def storeWaktu(
  id_laporan: Optional[str] = Query(None),
  id_karyawan: Optional[str] = Query(None)
):  
  try:
    pool = await get_db()

    async with pool.acquire() as conn:
      async with conn.cursor() as cursor:
        try:
          # 1. Start Transaction
          await conn.begin()

          q1 = "DELETE FROM laporan_ob WHERE id_laporan = %s AND id_karyawan = %s"
          await cursor.execute(q1, (id_laporan, id_karyawan))

          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "Sukses Delete Data"
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
    return JSONResponse(content={"status": "Errpr", "message": f"Koneksi Error {str(e)}"}, status_code=500)

@app.get('/ruanganbersihkan')
async def getMenu():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        q1 = "SELECT id, nama_ruangan, keterangan FROM kerja_ob_sementara"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Ruangan endpoint /list_room ": str(e)}, status_code=500)
  
@app.delete('/confirmkerjaanob')
async def deletefnb(
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
          q1 = "DELETE FROM kerja_ob_sementara WHERE id = %s"
          print("isi q1", data['id'])
          await cursor.execute(q1, (data['id'], ))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return "succes"
        except aiomysqlerror as e:
          # Rollback Input Jika Error
          error_details = traceback.format_exc()
          print(str(error_details))
          # Ambil Error code
          error_code = e.args[0] if e.args else "Unknown"
          
          await conn.rollback()
          return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
        except Exception as e:
          await conn.rollback()
          print(f"Error during insert : {e}")
          return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
  except Exception as e:
    error_details = traceback.format_exc()
    print(str(error_details))
    return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)

  


  

