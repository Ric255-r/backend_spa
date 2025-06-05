from typing import Optional

import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, Security, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
import pandas as pd
from aiomysql import Error as aiomysqlerror

app = APIRouter(prefix=("/pajak"))

@app.get('/getpajak')
async def getpajak():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

        q1 = "SELECT pajak FROM pajak"
        await cursor.execute(q1)

        row = await cursor.fetchone()
        return row[0]  # or just: return row[0] if appropriate

  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)

from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse

@app.put('/updatepajak')
async def updatepajak(request: Request):
    try:
        pool = await get_db()

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await conn.begin()

                    # Get JSON body
                    data = await request.json()
                    pajak = data.get('pajak')  # example: 0.35
                    id = 1  # hardcoded for now, you can replace with dynamic value

                    # Execute update query
                    q1 = "UPDATE pajak SET pajak = %s WHERE id = %s"
                    await cursor.execute(q1, (pajak, id))

                    await conn.commit()
                    return {"status": "success"}
                except Exception as e:
                    await conn.rollback()
                    return JSONResponse(
                        content={"status": "Error", "message": f"Server Error: {e}"},
                        status_code=500,
                    )
    except Exception as e:
        return JSONResponse(
            content={"status": "Error", "message": f"Koneksi Error: {str(e)}"},
            status_code=500,
        )
