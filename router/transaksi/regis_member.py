import re
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
import os
import shutil
import asyncio
import aiomysql

app = APIRouter(
  prefix="/member",
)

@app.post('/post_member')
async def postMember(
    nama: str = Form(...),
    no_hp: str = Form(...),
    status: str = Form(...),
    qr_code: UploadFile = File(...)
):
    try:
        pool = await get_db()

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    # 1. Start Transaction
                    await conn.begin()

                    # 2. Generate id_member
                    id_member = await generate_id_member_from_cursor(status, cursor)

                    # 3. Save QR Code Image
                    qr_folder = "qrcodes"
                    os.makedirs(qr_folder, exist_ok=True)
                    qr_path = f"{qr_folder}/{nama}_qrcode.png"

                    with open(qr_path, "wb") as buffer:
                        shutil.copyfileobj(qr_code.file, buffer)

                    # 4. Insert Data into `member` Table
                    q1 = "INSERT INTO member (id_member, nama, no_hp, status, id_gelang) VALUES (%s, %s, %s, %s, %s)"
                    await cursor.execute(q1, (id_member, nama, no_hp, status, qr_path))

                    # 5. Commit Transaction
                    await conn.commit()
                    await asyncio.sleep(0.2)

                    return JSONResponse(content={
                    "status": "Success",
                    "message": f"Data Berhasil Diinput dengan ID {id_member}",
                    "id_member": id_member  # ✅ This allows frontend to read it
                }, status_code=200)


                except aiomysql.Error as e:
                    await conn.rollback()
                    return JSONResponse(content={"status": "Error", "message": f"Database Error {e}"}, status_code=500)

                except Exception as e:
                    await conn.rollback()
                    return JSONResponse(content={"status": "Error", "message": f"Server Error {e}"}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)

async def generate_id_member_from_cursor(status: str, cursor) -> str:
    prefix = "MM" if status == "Member" else "MV"
    await cursor.execute(f"SELECT id_member FROM member WHERE id_member LIKE '{prefix}%'")
    rows = await cursor.fetchall()

    if rows:
        numbers = [int(re.search(r'\d+', row[0]).group()) for row in rows if re.search(r'\d+', row[0])]
        new_number = max(numbers) + 1
    else:
        new_number = 1

    return f"{prefix}{new_number:03d}"

@app.get('/id_member')
async def generate_id_member(status: str, db=Depends(get_db)):
    try:
        async with db.cursor() as cursor:
            id_member = await generate_id_member_from_cursor(status, cursor)

        return JSONResponse(content={
            "status": "Success",
            "id_member": id_member,
            "message": f"ID Member {id_member} berhasil dibuat"
        }, status_code=200)

    except Exception as e:
        return JSONResponse(content={"status": "Error", "message": f"Error Get id_member: {str(e)}"}, status_code=500)
