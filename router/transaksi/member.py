import asyncio
import json
from typing import Optional
import uuid
from fastapi import APIRouter, Query, Depends, File, Form, Request, HTTPException, Security, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from koneksi import get_db
from fastapi_jwt import (
  JwtAccessBearerCookie,
  JwtAuthorizationCredentials,
  JwtRefreshBearer
)
import pandas as pd
from aiomysql import Error as aiomysqlerror
from jwt_auth import access_security, refresh_security
import calendar
import time

# Untuk Routingnya jadi http://192.xx.xx.xx:5500/api/fnb/endpointfunction
app = APIRouter(
  prefix="/transmember",
  # dependencies=[Depends(verify_jwt)]
)

@app.get('/getpaket')
async def getPaket():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        # await asyncio.sleep(0.3)

        q1 = """
        SELECT 
    p.kode_promo,
    p.nama_promo,
    d.limit_kunjungan,
    d.harga_promo
    FROM promo p
    JOIN detail_promo_kunjungan d
    ON p.detail_kode_promo = d.detail_kode_promo
    WHERE p.detail_kode_promo LIKE 'DK%'
        """
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Paket Massage": str(e)}, status_code=500)

@app.get('/gettahunan')
async def getTahunan():
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        # await asyncio.sleep(0.3)

        q1 = """
        SELECT 
    p.kode_promo,
    p.nama_promo,
    d.jangka_tahun,
    d.harga_promo
FROM promo p
JOIN detail_promo_tahunan d
    ON p.detail_kode_promo = d.detail_kode_promo
WHERE p.detail_kode_promo LIKE 'DT%'
        """
        await cursor.execute(q1)

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')

  except Exception as e:
    return JSONResponse({"Error Get Paket Tahunan": str(e)}, status_code=500)
  
@app.post('/store')
async def storeData(request: Request):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await conn.begin()
                data = await request.json()
                
                # Validate required fields
                required_fields = ['id_member', 'id_transaksi', 'kode_promo', 'harga']
                for field in required_fields:
                    if field not in data:
                        raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
                
                try:
                    # Insert into detail_transaksi_member
                    new_id_dt = f"DT{uuid.uuid4().hex[:16]}"
                    q2 = """
                        INSERT INTO detail_transaksi_member(
                            id_detail_transaksi, id_transaksi, id_member, 
                            kode_promo, harga_promo, status
                        ) VALUES(%s, %s, %s, %s, %s, 'paid')
                    """
                    await cursor.execute(q2, (
                        new_id_dt, data['id_transaksi'], data['id_member'],
                        data['kode_promo'], data['harga']
                    ))
                    
                    # Update main_transaksi - always payment now ("awal")
                    q3_values = {
                        'jenis_transaksi': 'member',
                        'id_member': data['id_member'],
                        'no_hp': data['no_hp'],
                        'nama_tamu': data['nama_tamu'],
                        'total_harga': data.get('total_harga', data['harga']),
                        'disc': 0,
                        'grand_total': data.get('grand_total', data['harga']),
                        'jenis_pembayaran': False,  # Always "awal"
                        'status': 'paid',
                        'id_transaksi': data['id_transaksi']
                    }
                    
                    # Handle payment method
                    metode_pembayaran = data.get('metode_pembayaran', 'cash')
                    q3_values['metode_pembayaran'] = metode_pembayaran
                    
                    if metode_pembayaran in ['qris', 'debit']:
                        q3_values.update({
                            'nama_akun': data.get('nama_akun', ''),
                            'no_rek': data.get('no_rek', ''),
                            'nama_bank': data.get('nama_bank', ''),
                            'jumlah_bayar': data.get('jumlah_bayar', data['harga']),
                            'jumlah_kembalian': 0
                        })
                    else:  # cash
                        q3_values.update({
                            'jumlah_bayar': data.get('jumlah_bayar', data['harga']),
                            'jumlah_kembalian': data.get('jumlah_bayar', 0) - data['harga']
                        })
                    
                    q3 = """
                        UPDATE main_transaksi SET
                            jenis_transaksi = %(jenis_transaksi)s,
                            id_member = %(id_member)s,
                            no_hp = %(no_hp)s,
                            nama_tamu = %(nama_tamu)s,
                            total_harga = %(total_harga)s,
                            disc = %(disc)s,
                            grand_total = %(grand_total)s,
                            metode_pembayaran = %(metode_pembayaran)s,
                            jumlah_bayar = %(jumlah_bayar)s,
                            jumlah_kembalian = %(jumlah_kembalian)s,
                            jenis_pembayaran = %(jenis_pembayaran)s,
                            status = %(status)s
                        WHERE id_transaksi = %(id_transaksi)s
                    """

                    await cursor.execute(q3, q3_values)

                    q4 = """
                        UPDATE member SET
                        sisa_kunjungan = %s
                        WHERE id_member = %s
                    """
                    await cursor.execute(q4, (data['limit_kunjungan'], data['id_member']))
                    
                    await conn.commit()
                    return {"status": "Success", "message": "Payment processed successfully"}
                    
                except Exception as e:
                    await conn.rollback()
                    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
                    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")