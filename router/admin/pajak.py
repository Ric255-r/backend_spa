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

        q1 = "SELECT * FROM pajak"
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Latest Trans": str(e)}, status_code=500)


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
                    pajakmsg = data.get('pajak_msg')
                    pajakfnb = data.get('pajak_fnb') 
                    id = 1  # hardcoded for now, you can replace with dynamic value

                    # Execute update query
                    q1 = "UPDATE pajak SET pajak_msg = %s, pajak_fnb = %s WHERE id = %s"
                    await cursor.execute(q1, (pajakmsg, pajakfnb, id))

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
