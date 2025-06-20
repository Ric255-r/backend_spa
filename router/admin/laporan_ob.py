import json
from typing import Optional
import uuid
import aiomysql
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

app = APIRouter(
  prefix="/laporan",
)

@app.get('/laporanob')
async def getLaporanOb():
    try:
        pool = await get_db()  # Ensure this returns aiomysql pool or compatible
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
                q1 = """
                    SELECT lo.*, DATE_FORMAT(lo.created_at, '%d/%m/%Y') AS formatted_date, r.nama_ruangan 
                    FROM laporan_ob lo 
                    INNER JOIN ruangan r ON lo.id_ruangan = r.id_ruangan
                    WHERE (lo.laporan IS NOT NULL AND lo.laporan != '')
                    OR (lo.foto_laporan IS NOT NULL AND lo.foto_laporan != '')
                """
                await cursor.execute(q1)
                items = await cursor.fetchall()

                column_name = [col[0] for col in cursor.description]
                df = pd.DataFrame(items, columns=column_name)

                # Safely parse foto_laporan JSON strings
                def safe_json_loads(x):
                    try:
                        if isinstance(x, str) and x.strip():
                            return json.loads(x)
                    except Exception:
                        pass
                    return []

                df["foto_laporan"] = df["foto_laporan"].apply(safe_json_loads)

                # Convert dataframe to list of dict (JSON serializable)
                result = df.to_dict(orient='records')
                return result

    except Exception as e:
        # Log the error somewhere or print for debug
        print(f"Error in getLaporanOb: {e}")
        return JSONResponse({"error": "Failed to get laporan ob", "detail": str(e)}, status_code=500)

@app.put("/updatelaporanob/{id_laporan}")
async def update_laporan_ob(id_laporan: str):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Get current laporan + related id_ruangan
                await cursor.execute("""
                    SELECT lo.is_solved, lo.id_ruangan 
                    FROM laporan_ob lo
                    LEFT JOIN ruangan r ON lo.id_ruangan = r.id_ruangan
                    WHERE lo.id_laporan = %s
                """, (id_laporan,))

                data = await cursor.fetchone()

                if not data:
                    raise HTTPException(status_code=404, detail="Laporan not found")

                current_status = data['is_solved']
                id_ruangan = data['id_ruangan']
                new_status = 0 if current_status == 1 else 1

                # Update laporan status
                await cursor.execute("""
                    UPDATE laporan_ob
                    SET is_solved = %s
                    WHERE id_laporan = %s
                """, (new_status, id_laporan))

                # Update ruangan status based on new is_solved
                ruangan_status = "aktif" if new_status == 1 else "maintenance"
                await cursor.execute("""
                    UPDATE ruangan
                    SET status = %s
                    WHERE id_ruangan = %s
                """, (ruangan_status, id_ruangan))

                await conn.commit()

                return {"message": "Laporan status updated", "new_status": new_status}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



# @app.put('/update_pekerja/{id_karyawan}')
# async def putPekerja(
#   id_karyawan: str,
#   request: Request
# ):
#   try:
#     pool = await get_db()

#     async with pool.acquire() as conn:
#       async with conn.cursor() as cursor:
#         try:
#           # 1. Start Transaction
#           await conn.begin()

#           # 2. Execute querynya
#           data = await request.json()
#           # await cursor.execute("SELECT FROM karyawan WHERE id_karyawan = %s", (data['id_karyawan'],))
#           # exists = await cursor.fetchone()

#           # if not exists:
#           #     await conn.rollback()
#           #     return JSONResponse(content={"status": "Error", "message": "Karyawan not found"}, status_code=404)
          
#           q1 = "UPDATE karyawan SET nik = %s, nama_karyawan = %s, alamat = %s, jk = %s, no_hp = %s, status = %s WHERE id_karyawan = %s"
#           await cursor.execute(q1, (data['nik'], data['nama_karyawan'], data['alamat'], data['jk'], data['no_hp'], data['status'], id_karyawan)) 
#           # 3. Klo Sukses, dia bkl save ke db
#           await conn.commit()

#           return JSONResponse(content={"status": "Success", "message": "Data Berhasil Diupdate"}, status_code=200)
#         except aiomysqlerror as e:
#           # Rollback Input Jika Error

#           # Ambil Error code
#           error_code = e.args[0] if e.args else "Unknown"
          
#           await conn.rollback()
#           return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
#         except Exception as e:
#           await conn.rollback()
#           return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
#   except Exception as e:
#     return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)
  
# @app.delete('/delete_pekerja/{id_karyawan}')
# async def deletePekerja(
#   id_karyawan: str,
#   request: Request
# ):
#   try:
#     pool = await get_db()

#     async with pool.acquire() as conn:
#       async with conn.cursor() as cursor:
#         try:
#           # 1. Start Transaction
#           await conn.begin()

#           # 2. Execute querynya
#           data = await request.json()
          
#           q1 = "DELETE FROM karyawan WHERE id_karyawan = %s"
#           await cursor.execute(q1, (id_karyawan)) 
#           # 3. Klo Sukses, dia bkl save ke db
#           await conn.commit()

#           return JSONResponse(content={"status": "Success", "message": "Data Berhasil Dihapus"}, status_code=200)
#         except aiomysqlerror as e:
#           # Rollback Input Jika Error

#           # Ambil Error code
#           error_code = e.args[0] if e.args else "Unknown"
          
#           await conn.rollback()
#           return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
#         except Exception as e:
#           await conn.rollback()
#           return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
#   except Exception as e:
#     return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)

# @app.get('/caripekerja')
# async def cariPekerja(
#   request: Request
# ):
#   try:
#     pool = await get_db()

#     async with pool.acquire() as conn:
#       async with conn.cursor() as cursor:
#         try:
#           # 1. Start Transaction
#           await conn.begin()

#           # 2. Execute querynya
#           data = await request.json()
#           q1 = "SELECT * FROM karyawan WHERE nama_karyawan LIKE %s"
#           await cursor.execute(q1, (data['nama_karyawan'])) 
#           # 3. Klo Sukses, dia bkl save ke db
          
#           items = await cursor.fetchall()

#           column_name = []
#           for kol in cursor.description:
#             column_name.append(kol[0])

#           df = pd.DataFrame(items, columns=column_name)
#           return df.to_dict('records')

#           return JSONResponse(content={"status": "Success", "message": "Data Berhasil Dicari"}, status_code=200)
#         except aiomysqlerror as e:
#           # Rollback Input Jika Error

#           # Ambil Error code
#           error_code = e.args[0] if e.args else "Unknown"
          
#           await conn.rollback()
#           return JSONResponse(content={"status": "Error", "message": f"Database Error{e} "}, status_code=500)
        
#         except Exception as e:
#           await conn.rollback()
#           return JSONResponse(content={"status": "Error", "message": f"Server Error {e} "}, status_code=500)
        
#   except Exception as e:
#     return JSONResponse(content={"status": "Error", "message": f"Koneksi Error {str(e)}"}, status_code=500)