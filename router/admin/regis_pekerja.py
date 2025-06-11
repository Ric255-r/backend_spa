import os
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
from typing import List
import pandas as pd
from aiomysql import Error as aiomysqlerror
from fastapi import FastAPI, Request, UploadFile, File, Form
import base64
from pathlib import Path
import aiofiles

KONTRAK_DIR = "kontrak"
os.makedirs(KONTRAK_DIR, exist_ok=True)

app = APIRouter(
  prefix="/pekerja",
)
    
@app.get('/getIdKaryawan/{jabatan}')
async def getIdKaryawan(jabatan: str):  # Accept 'category' as a parameter
    try:
        pool = await get_db()  # Get the database connection pool

        # Map the categories to their prefixes
        prefix_mapping = {
            "terapis": "T",
            "resepsionis": "R",
            "supervisor": "S",
            "office boy": "O",
            "admin": "A",
            "kitchen": "K",
            "gro": "G",
        }

        # Get the prefix for the selected category
        prefix = prefix_mapping.get(jabatan)
        if not prefix:
            return JSONResponse({"error": "Invalid category"}, status_code=400)

        async with pool.acquire() as conn:  # Auto release connection
            async with conn.cursor() as cursor:
                await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
                # Query the latest ID for the given category
                query = f"""
                SELECT id_karyawan 
                FROM karyawan 
                WHERE id_karyawan LIKE '{prefix}%' 
                ORDER BY id_karyawan DESC 
                LIMIT 1
                """
                await cursor.execute(query)

                result = await cursor.fetchone()
                latest_id = result[0] if result else None

                # Generate the next ID
                if latest_id is None:
                    new_id = f"{prefix}001"  # Start from 001 if no existing records
                else:
                    num = int(latest_id[1:]) + 1  # Extract number, increment
                    new_id = f"{prefix}{str(num).zfill(3)}"  # Zero-pad to 3 digits

                return new_id

    except Exception as e:
        return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)

@app.post('/post_pekerja')
async def postPekerja(
    id_karyawan: str = Form(...),
    nik: str = Form(...),
    nama_karyawan: str = Form(...),
    alamat: str = Form(...),
    jk: str = Form(...),
    no_hp: str = Form(...),
    jabatan: str = Form(...),
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
                    if kontrak_img:  # ⬅️ Add this check
                        for file in kontrak_img:
                            filename = f"{uuid.uuid4()}_{file.filename}"
                            file_path = Path(KONTRAK_DIR) / filename

                            async with aiofiles.open(file_path, 'wb') as out_file:
                                content = await file.read()
                                await out_file.write(content)

                            filenames.append(filename)

                    kontrak_str = ",".join(filenames) if filenames else ""

                    # Insert into DB
                    q1 = """
                        INSERT INTO karyawan 
                        (id_karyawan, nik, nama_karyawan, alamat, jk, no_hp, jabatan, status, kontrak_img) 
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(q1, (
                        id_karyawan, nik, nama_karyawan, alamat, jk, no_hp, jabatan, status, kontrak_str
                    ))

                    await conn.commit()

                    return JSONResponse(
                        content={"status": "Success", "message": "Data Berhasil Diinput"},
                        status_code=200
                    )

                except Exception as e:
                    await conn.rollback()
                    return JSONResponse(
                        content={"status": "Error", "message": f"Server Error: {e}"},
                        status_code=500
                    )

    except Exception as e:
        return JSONResponse(
            content={"status": "Error", "message": f"Koneksi Error: {str(e)}"},
            status_code=500
        )
  
@app.post('/post_ob')
async def postOb(
    id_karyawan: str = Form(...),
    nik: str = Form(...),
    nama_karyawan: str = Form(...),
    alamat: str = Form(...),
    jk: str = Form(...),
    no_hp: str = Form(...),
    jabatan: str = Form(...),
    status: str = Form(...),
    senin: int = Form(...),
    selasa: int = Form(...),
    rabu: int = Form(...),
    kamis: int = Form(...),
    jumat: int = Form(...),
    sabtu: int = Form(...),
    minggu: int = Form(...),
    kontrak_img: List[UploadFile] = File(None)  # Make it optional
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
                            if not file.filename:
                                continue

                            filename = f"{uuid.uuid4()}_{file.filename}"
                            file_path = Path(KONTRAK_DIR) / filename

                            async with aiofiles.open(file_path, 'wb') as out_file:
                                content = await file.read()
                                await out_file.write(content)

                            filenames.append(filename)

                    kontrak_str = ",".join(filenames) if filenames else None

                    # Insert into karyawan
                    q1 = """
                        INSERT INTO karyawan 
                        (id_karyawan, nik, nama_karyawan, alamat, jk, no_hp, jabatan, status, kontrak_img)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(q1, (
                        id_karyawan, nik, nama_karyawan, alamat, jk, no_hp, jabatan, status, kontrak_str
                    ))

                    # Insert into hari_kerja_ob
                    q2 = """
                        INSERT INTO hari_kerja_ob 
                        (kode_ob, senin, selasa, rabu, kamis, jumat, sabtu, minggu)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(q2, (
                        id_karyawan, senin, selasa, rabu, kamis, jumat, sabtu, minggu
                    ))

                    await conn.commit()

                    return JSONResponse(
                        content={"status": "Success", "message": "Data Berhasil Diinput"},
                        status_code=200
                    )

                except Exception as e:
                    await conn.rollback()
                    return JSONResponse(
                        content={"status": "Error", "message": f"Server Error: {e}"},
                        status_code=500
                    )

    except Exception as e:
        return JSONResponse(
            content={"status": "Error", "message": f"Koneksi Error: {str(e)}"},
            status_code=500
        )
  
@app.post('/post_terapis')
async def postTerapis(
    id_karyawan: str = Form(...),
    nik: str = Form(...),
    nama_karyawan: str = Form(...),
    alamat: str = Form(...),
    jk: str = Form(...),
    no_hp: str = Form(...),
    jabatan: str = Form(...),
    status: str = Form(...),
    senin: int = Form(...),
    selasa: int = Form(...),
    rabu: int = Form(...),
    kamis: int = Form(...),
    jumat: int = Form(...),
    sabtu: int = Form(...),
    minggu: int = Form(...),
    kontrak_img: List[UploadFile] = File(None)  # Optional upload
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
                            if not file.filename:
                                continue

                            filename = f"{uuid.uuid4()}_{file.filename}"
                            file_path = Path(KONTRAK_DIR) / filename

                            async with aiofiles.open(file_path, 'wb') as out_file:
                                content = await file.read()
                                await out_file.write(content)

                            filenames.append(filename)

                    kontrak_str = ",".join(filenames) if filenames else None

                    # Insert into karyawan
                    q1 = """
                        INSERT INTO karyawan 
                        (id_karyawan, nik, nama_karyawan, alamat, jk, no_hp, jabatan, status, kontrak_img)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(q1, (
                        id_karyawan, nik, nama_karyawan, alamat, jk, no_hp, jabatan, status, kontrak_str
                    ))

                    # Insert into hari_kerja_terapis
                    q2 = """
                        INSERT INTO hari_kerja_terapis 
                        (kode_terapis, senin, selasa, rabu, kamis, jumat, sabtu, minggu)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(q2, (
                        id_karyawan, senin, selasa, rabu, kamis, jumat, sabtu, minggu
                    ))

                    await conn.commit()

                    return JSONResponse(
                        content={"status": "Success", "message": "Data Berhasil Diinput"},
                        status_code=200
                    )

                except Exception as e:
                    await conn.rollback()
                    return JSONResponse(
                        content={"status": "Error", "message": f"Server Error: {e}"},
                        status_code=500
                    )

    except Exception as e:
        return JSONResponse(
            content={"status": "Error", "message": f"Koneksi Error: {str(e)}"},
            status_code=500
        )
# async def getIdKaryawan():
#   try:
#     pool = await get_db() # Get The pool

#     async with pool.acquire() as conn:  # Auto Release
#       async with conn.cursor() as cursor:

#         q1 = "SELECT id_karyawan FROM karyawan"
#         await cursor.execute(q1)

#         items = await cursor.fetchone() #id transaksi terletak di index ke-0
#         id_karyawan = items[0] if items is not None else None

#         if id_karyawan is None:
#           num = "1"
#           strpad = "P" + num.zfill(3)
#         else:
#           getNum = id_produk[1:]
#           num = int(getNum) + 1
#           strpad = "P" + str(num).zfill(3)

#         return strpad


#   except Exception as e:
#     return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)