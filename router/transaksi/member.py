import asyncio
import json
from typing import Optional
import uuid
import aiomysql
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
    d.harga_promo,
    d.limit_promo
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
  
@app.post('/storekunjungan')
async def storeData(request: Request):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
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
                            kode_promo, harga_promo, status, sisa_kunjungan, exp_kunjungan
                        ) VALUES(%s, %s, %s, %s, %s, 'paid', %s, %s)
                    """
                    await cursor.execute(q2, (
                        new_id_dt, data['id_transaksi'], data['id_member'],
                        data['kode_promo'], data['harga'], data['limit_kunjungan'], data['exp_kunjungan']
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
                    if metode_pembayaran in ['qris', 'debit', 'kredit']:
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
                    
                    q1 = """
                        SELECT * FROM pajak LIMIT 1
                    """
                    await cursor.execute(q1)
                    item_q1 = await cursor.fetchone()
                    pjk = item_q1['pajak_msg'] * data.get('grand_total') + data.get('grand_total')
                    print(pjk)
                    q3 = f"""
                        UPDATE main_transaksi SET
                            jenis_transaksi = %(jenis_transaksi)s,
                            id_member = %(id_member)s,
                            no_hp = %(no_hp)s,
                            nama_tamu = %(nama_tamu)s,
                            total_harga = %(total_harga)s,
                            disc = %(disc)s,
                            grand_total = %(grand_total)s,
                            pajak = {item_q1['pajak_msg']},
                            gtotal_stlh_pajak = {pjk},
                            metode_pembayaran = %(metode_pembayaran)s,
                            {"""
                                nama_akun = %(nama_akun)s,
                                no_rek = %(no_rek)s,
                                nama_bank = %(nama_bank)s,
                            """ if metode_pembayaran != "cash" else ""}
                            jumlah_bayar = %(jumlah_bayar)s,
                            jumlah_kembalian = %(jumlah_kembalian)s,
                            jenis_pembayaran = %(jenis_pembayaran)s,
                            status = %(status)s
                        WHERE id_transaksi = %(id_transaksi)s
                    """
                    print("isi q3", q3)
                    print(q3_values)
                    await cursor.execute(q3, q3_values)

                    qPayment = """
                        INSERT INTO pembayaran_transaksi(
                        id_transaksi, metode_pembayaran, nama_akun, no_rek, nama_bank, jumlah_bayar, keterangan
                        )
                        VALUES(%s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(qPayment, (
                        data['id_transaksi'], 
                        data.get('metode_pembayaran', "-"), 
                        data.get('nama_akun', "-"),
                        data.get('no_rek', '-'),
                        data.get('nama_bank', '-'),
                        data.get('grand_total', data['harga']),
                        data.get('keterangan', '-'),
                    ))
                    
                    await conn.commit()
                    return {"status": "Success", "message": "Payment processed successfully"}
                    
                except Exception as e:
                    await conn.rollback()
                    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
                    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post('/storetahunan')
async def store_tahunan(request: Request):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await conn.begin()
                data = await request.json()

                # Validate required fields
                required = ['id_member', 'id_transaksi', 'kode_promo', 'harga', 'exp_tahunan']
                for field in required:
                    if field not in data:
                        raise HTTPException(status_code=400, detail=f"Missing field: {field}")

                try:
                    # Insert into detail_transaksi_member (promo tahunan)
                    new_id_dt = f"DT{uuid.uuid4().hex[:16]}"
                    q_insert = """
                        INSERT INTO detail_transaksi_member(
                            id_detail_transaksi, id_transaksi, id_member, 
                            kode_promo, harga_promo, status, exp_tahunan
                        ) VALUES(%s, %s, %s, %s, %s, 'paid', %s)
                    """
                    await cursor.execute(q_insert, (
                        new_id_dt, data['id_transaksi'], data['id_member'],
                        data['kode_promo'], data['harga'], data['exp_tahunan']
                    ))

                    # Prepare values for updating main_transaksi
                    q_values = {
                        'id_member': data['id_member'],
                        'no_hp': data.get('no_hp', ''),
                        'nama_tamu': data.get('nama_tamu', ''),
                        'total_harga': data['harga'],
                        'disc': 0,
                        'grand_total': data['harga'],
                        'jenis_pembayaran': False,
                        'status': 'paid',
                        'id_transaksi': data['id_transaksi'],
                        'metode_pembayaran': data.get('metode_pembayaran', 'cash'),
                        'nama_akun': '',
                        'no_rek': '',
                        'nama_bank': '',
                        'jumlah_bayar': data.get('jumlah_bayar', data['harga']),
                        'jumlah_kembalian': 0
                    }

                    metode = q_values['metode_pembayaran']
                    if metode == 'cash':
                        q_values['jumlah_kembalian'] = data.get('jumlah_bayar', 0) - data['harga']
                    elif metode in ['qris', 'debit', 'kredit']:
                        q_values['nama_akun'] = data.get('nama_akun', '')
                        q_values['no_rek'] = data.get('no_rek', '')
                        q_values['nama_bank'] = data.get('nama_bank', '')

                    q_update = """
                        UPDATE main_transaksi SET
                            jenis_transaksi = 'member',
                            id_member = %(id_member)s,
                            no_hp = %(no_hp)s,
                            nama_tamu = %(nama_tamu)s,
                            total_harga = %(total_harga)s,
                            disc = %(disc)s,
                            grand_total = %(grand_total)s,
                            metode_pembayaran = %(metode_pembayaran)s,
                            nama_akun = %(nama_akun)s,
                            no_rek = %(no_rek)s,
                            nama_bank = %(nama_bank)s,
                            jumlah_bayar = %(jumlah_bayar)s,
                            jumlah_kembalian = %(jumlah_kembalian)s,
                            jenis_pembayaran = %(jenis_pembayaran)s,
                            status = %(status)s
                        WHERE id_transaksi = %(id_transaksi)s
                    """
                    await cursor.execute(q_update, q_values)

                    qPayment = """
                        INSERT INTO pembayaran_transaksi(
                        id_transaksi, metode_pembayaran, nama_akun, no_rek, nama_bank, jumlah_bayar, keterangan
                        )
                        VALUES(%s, %s, %s, %s, %s, %s, %s)
                    """
                    await cursor.execute(qPayment, (
                        data['id_transaksi'], 
                        data.get('metode_pembayaran', "-"), 
                        data.get('nama_akun', "-"),
                        data.get('no_rek', '-'),
                        data.get('nama_bank', '-'),
                        data['gtotal_stlh_pajak'],
                        data.get('keterangan', '-'),
                    ))

                    await conn.commit()
                    return {"status": "Success", "message": "Tahunan promo applied"}

                except Exception as e:
                    await conn.rollback()
                    raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/checkpromo")
async def check_promo(id_member: str):
    try:
        pool = await get_db()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""
                    SELECT * FROM detail_transaksi_member
                    WHERE id_member = %s AND exp_tahunan >= CURDATE()
                """, (id_member,))
                result = await cursor.fetchone()
                return {"has_promo": result is not None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))