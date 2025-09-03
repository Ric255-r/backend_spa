import os
import traceback
from typing import List, Optional
import uuid
import aiofiles
import aiomysql
from fastapi import APIRouter, Depends, File, Form, Path, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from urllib.parse import unquote
from pathlib import Path as FilePath  # ✅ Ini yang benar untuk path manipulasi
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
from fastapi.responses import FileResponse
from fastapi import HTTPException
import pandas as pd
from aiomysql import Error as aiomysqlerror

KONTRAK_DIR = os.path.abspath("kontrak")

app = APIRouter(
  prefix="/listpekerja",
)

@app.get('/datapekerja')
async def getDataPekerja():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT * FROM karyawan"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Karyawan": str(e)}, status_code=500)
  
# Ini Utk transaksi
@app.get('/dataterapis')
async def getDataTerapis():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT * FROM karyawan WHERE (jabatan = %s or id_karyawan LIKE %s) AND status = 'aktif'"
        await cursor.execute(q1, ("terapis", "T%"))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Terapis": str(e)}, status_code=500)
  
@app.get('/dataterapisrolling')
async def getDataTerapisRolling():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT k.*, a.jam_absen FROM karyawan k JOIN absensi_terapis a ON k.id_karyawan = a.id_karyawan WHERE k.jabatan = %s OR k.id_karyawan LIKE %s ORDER BY a.jam_absen ASC;"
        await cursor.execute(q1, ("terapis", "T%"))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data Terapis": str(e)}, status_code=500)
  
@app.get('/datagro')
async def getDataGro():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT * FROM karyawan WHERE jabatan = %s or id_karyawan LIKE %s"
        await cursor.execute(q1, ("gro", "G%"))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data GRO": str(e)}, status_code=500)

# End Utk Transaksi

@app.post('/update_pekerja')
async def update_pekerja(
    id_karyawan: str = Form(...),
    nik: str = Form(...),
    nama_karyawan: str = Form(...),
    alamat: str = Form(...),
    jk: str = Form(...),
    no_hp: str = Form(...),
    status: str = Form(...),
    kontrak_img: Optional[List[UploadFile]] = File(None)
):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await conn.begin()

                    filenames = []
                    if kontrak_img:
                        for file in kontrak_img:
                            filename = f"{uuid.uuid4()}_{file.filename}"
                            file_path = FilePath(KONTRAK_DIR) / filename

                            async with aiofiles.open(file_path, 'wb') as out_file:
                                content = await file.read()
                                await out_file.write(content)

                            filenames.append(filename)

                    kontrak_str = ",".join(filenames) if filenames else ""

                    # Update query
                    q1 = """
                        UPDATE karyawan SET
                            nik = %s,
                            nama_karyawan = %s,
                            alamat = %s,
                            jk = %s,
                            no_hp = %s,
                            status = %s,
                            kontrak_img = %s
                        WHERE id_karyawan = %s
                    """
                    await cursor.execute(q1, (
                        nik, nama_karyawan, alamat, jk, no_hp, status, kontrak_str, id_karyawan
                    ))

                    await conn.commit()
                    return JSONResponse(content={"status": "Success", "message": "Data berhasil diupdate"}, status_code=200)

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    await conn.rollback()
                    return JSONResponse(content={"status": "Error", "message": f"Server Error: {e}"}, status_code=500)
    except Exception as e:
      import traceback
      traceback.print_exc()  # ⬅️ Ini akan menunjukkan error detail di terminal
      return JSONResponse(
          content={"status": "Error", "message": f"Koneksi Error: {e}"},
          status_code=500
    )

  
@app.delete('/delete_pekerja/{id_karyawan}')
async def deletePekerja(
  id_karyawan: str,
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
          
          q1 = "DELETE FROM karyawan WHERE id_karyawan = %s"
          await cursor.execute(q1, (id_karyawan)) 
          q2 = "DELETE FROM users WHERE id_karyawan = %s"
          await cursor.execute(q2, (id_karyawan))
          # 3. Klo Sukses, dia bkl save ke db
          await conn.commit()

          return JSONResponse(content={"status": "Success", "message": "Data Berhasil Dihapus"}, status_code=200)
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

@app.get('/caripekerja')
async def cariPekerja(
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
          q1 = "SELECT * FROM karyawan WHERE nama_karyawan LIKE %s"
          await cursor.execute(q1, (data['nama_karyawan'])) 
          # 3. Klo Sukses, dia bkl save ke db
          
          items = await cursor.fetchall()

          column_name = []
          for kol in cursor.description:
            column_name.append(kol[0])

          df = pd.DataFrame(items, columns=column_name)
          return df.to_dict('records')

          return JSONResponse(content={"status": "Success", "message": "Data Berhasil Dicari"}, status_code=200)
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


@app.get('/dataTampilanTerapis')
async def getDataGro():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        q1 = "SELECT * FROM karyawan WHERE (jabatan = %s or id_karyawan LIKE %s) AND status = 'aktif' ORDER BY is_occupied ASC" 
        await cursor.execute(q1, ("terapis", "T%",))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Data GRO": str(e)}, status_code=500)

@app.post("/update_occupied")
async def update_occupied(request: Request):
  try:
    data = await request.json()
    print("Data diterima:", data)

    id_karyawan = data.get("id_karyawan")
    is_occupied = data.get("is_occupied")

    if id_karyawan is None:
        raise HTTPException(status_code=400, detail="Missing id_karyawan")

    if is_occupied is None:
        raise HTTPException(status_code=400, detail="Missing is_occupied")

    pool = await get_db()
    async with pool.acquire() as conn:
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        await conn.begin()

        query = "UPDATE karyawan SET is_occupied = %s WHERE id_karyawan = %s"
        print("Executing query:", query, (is_occupied, id_karyawan))
        await cursor.execute(query, (is_occupied, id_karyawan))

        query2 = "SELECT * FROM main_transaksi WHERE id_karyawan = %s ORDER BY created_at DESC LIMIT 1"
        await cursor.execute(query2, (id_karyawan, ))
        item2 = await cursor.fetchone()

        query3 = "DELETE FROM durasi_kerja_sementara WHERE id_transaksi = %s"
        await cursor.execute(query3, (item2['id_transaksi'], ))
        await conn.commit()

      return {"message": "Berhasil update is_occupied"}
  
  except HTTPException as e:
    await conn.rollback()
    return JSONResponse(content={"Status": f"Error {str(e)}"}, status_code=e.status_code)

  except aiomysqlerror as e:
    await conn.rollback()
    return JSONResponse(content={"status": "error", "message": f"Database Error {str(e)}"}, status_code=500)
  
  except Exception as e:
    print("Exception occurred:", str(e))
    traceback.print_exc()
    raise HTTPException(status_code=500, detail="Internal Server Error")