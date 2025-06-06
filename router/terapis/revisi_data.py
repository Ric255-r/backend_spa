from datetime import datetime
import json
from typing import Optional
import uuid
import aiomysql
from fastapi import APIRouter, File, Form, Query, Request, HTTPException, Security, UploadFile
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
from datetime import timedelta
from router.terapis.kamar_terapis import kamar_connection

app = APIRouter(
  prefix="/revisi"
)

@app.get('/transaksi')
async def getLatestTrans(
  id_transaksi: str = Query()
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor() as cursor:
        await cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        q1 = "SELECT * FROM main_transaksi WHERE id_transaksi = %s"
        await cursor.execute(q1, (id_transaksi, ))

        items = await cursor.fetchall()

        column_name = []
        for kol in cursor.description:
          column_name.append(kol[0])

        df = pd.DataFrame(items, columns=column_name)
        return df.to_dict('records')[0]

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  
@app.put('/terapis')
async def updateTerapis(
  request: Request,
  id_transaksi: str = Query(),
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
          await conn.begin()

          data = await request.json()
          prev_terapis = data['current_terapis']
          new_terapis = data['new_terapis']

          q1 = "UPDATE main_transaksi SET id_terapis = %s, sedang_dikerjakan = 0 WHERE id_transaksi = %s"
          await cursor.execute(q1, (new_terapis, id_transaksi))

          q2 = "UPDATE terapis_kerja SET is_cancel = 1, is_tunda = 0, jam_selesai = NOW() WHERE id_transaksi = %s AND id_terapis = %s"
          await cursor.execute(q2, (id_transaksi, prev_terapis))

          q3 = "UPDATE karyawan SET is_occupied = 0 WHERE id_karyawan = %s"
          await cursor.execute(q3, (prev_terapis, ))

          q4 = "UPDATE karyawan SET is_occupied = 1 WHERE id_karyawan = %s"
          await cursor.execute(q4, (new_terapis, ))

          await conn.commit()

          qSelectMain = "SELECT * FROM main_transaksi WHERE id_transaksi = %s"
          await cursor.execute(qSelectMain, (id_transaksi, ))
          item_main = await cursor.fetchone()

          qSelectTerapis = "SELECT * FROM karyawan WHERE id_karyawan = %s"
          await cursor.execute(qSelectTerapis, (item_main['id_terapis'], ))
          item_terapis = await cursor.fetchone()

          qSelectRuangan = "SELECT nama_ruangan FROM ruangan WHERE id_ruangan = %s"
          await cursor.execute(qSelectRuangan, (item_main['id_ruangan'], ))
          item_ruangan = await cursor.fetchone()

          # Ini utk aktifkan websocket kirim ke admin
          for ws_con in kamar_connection:
            await ws_con.send_text(
              json.dumps({
                "id_transaksi": id_transaksi,
                "status": "ganti_terapis",
                "message": f"Ruangan {item_ruangan['nama_ruangan']} Mengganti Terapis ke {item_terapis['nama_karyawan']}"
              })
            )

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"Error Mysql": str(e)}, status_code=500)
        
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Error HTTP": str(e.detail)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  
@app.put('/ruangan')
async def updateRuangan(
  request: Request
):
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
          await conn.begin()

          data = await request.json()
          id_transaksi = data['id_transaksi']
          prev_kode_ruangan = data['prev_kode_ruangan']
          new_kode_ruangan = data['new_kode_ruangan']

          qSelect = "SELECT id_ruangan FROM ruangan WHERE id_karyawan = %s"
          await cursor.execute(qSelect, (new_kode_ruangan, ))
          items = await cursor.fetchone()

          q1 = "UPDATE main_transaksi SET id_ruangan = %s, sedang_dikerjakan = 0 WHERE id_transaksi = %s"
          await cursor.execute(q1, (items['id_ruangan'], id_transaksi))

          q2 = "UPDATE terapis_kerja SET is_tunda = 1 WHERE id_transaksi = %s"
          await cursor.execute(q2, (id_transaksi))

          q3 = "UPDATE ruangan SET status = 'aktif' WHERE id_karyawan = %s"
          await cursor.execute(q3, (prev_kode_ruangan, ))

          q4 = "UPDATE ruangan SET status = 'occupied' WHERE id_karyawan = %s"
          await cursor.execute(q4, (new_kode_ruangan, ))

          q5 = "UPDATE durasi_kerja_sementara SET kode_ruangan = %s WHERE id_transaksi = %s"
          await cursor.execute(q5, (new_kode_ruangan, id_transaksi))

          await conn.commit()

          qSelectMain = "SELECT * FROM main_transaksi WHERE id_transaksi = %s"
          await cursor.execute(qSelectMain, (id_transaksi, ))
          item_main = await cursor.fetchone()

          qSelectRuangan = "SELECT nama_ruangan FROM ruangan WHERE id_ruangan = %s"
          await cursor.execute(qSelectRuangan, (item_main['id_ruangan'], ))
          item_ruangan = await cursor.fetchone()

          # Ini utk aktifkan websocket kirim ke admin
          for ws_con in kamar_connection:
            await ws_con.send_text(
              json.dumps({
                "id_transaksi": id_transaksi,
                "status": "ganti_ruangan",
                "message": f"Transaksi/Loker {item_main['id_transaksi']} / {item_main['no_loker']} mengganti ruangan ke {item_ruangan['nama_ruangan']} "
              })
            )
        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"Error Mysql": str(e)}, status_code=500)
        
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Error HTTP": str(e.detail)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)

@app.post('/tambahpaket_produk')
async def addon(
  request: Request,
):
  promo_index_store = {}
  try:
    pool = await get_db() # Get The pool

    async with pool.acquire() as conn:  # Auto Release
      async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
          await conn.begin()

          data = await request.json()
          id_trans = data['id_transaksi']

          details = data.get('detail_trans', [])
          print('detail adalah :', details)
          total_addon = 0
          total_durasi_global = 0
          for item in details:
            new_id_dt = f"DT{uuid.uuid4().hex[:16]}".upper()
            total_addon += item['harga_total']

            if item['satuan'].lower() == "pcs":
              total_durasi = item['jlh'] * item['durasi_awal']
              total_durasi_global += total_durasi

              q2 = """
                INSERT INTO detail_transaksi_produk(
                  id_detail_transaksi, id_transaksi, id_produk, qty, satuan, durasi_awal, 
                  total_durasi, harga_item, harga_total, status, is_addon
                ) 
                VALUES(
                  %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s
                )
              """
              await cursor.execute(q2, 
                (new_id_dt, id_trans, item['id_paket_msg'], item['jlh'], item['satuan'], item['durasi_awal'],
                total_durasi, item['harga_paket_msg'], item['harga_total'], item['status'], item['is_addon'])
              )
            else:
              total_durasi = item['jlh'] * item['durasi_awal']
              total_durasi_global += total_durasi

              q2 = """
                INSERT INTO detail_transaksi_paket(
                  id_detail_transaksi, id_transaksi, id_paket, qty, satuan, durasi_awal, 
                  total_durasi, harga_item, harga_total, status, is_addon
                ) 
                VALUES(
                  %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s
                )
              """
              await cursor.execute(q2, (
                new_id_dt, id_trans, item['id_paket_msg'], item['jlh'], item['satuan'], item['durasi_awal'],
                total_durasi, item['harga_paket_msg'], item['harga_total'], item['status'], item['is_addon']
              ))

            q_getnamapromo = "SELECT nama_paket_msg FROM paket_massage WHERE id_paket_msg = %s"
            await cursor.execute(q_getnamapromo, (item['id_paket_msg'],))
            nama_paket = await cursor.fetchone()
            print('nama paket', nama_paket)
              
            if item['harga_paket_msg'] == 0:

                q_check = """
                    SELECT DISTINCT dtm.id_member, dtm.kode_promo 
                    FROM detail_transaksi_member dtm
                    JOIN promo p ON dtm.kode_promo = p.kode_promo
                    JOIN detail_promo_kunjungan dpk ON dpk.detail_kode_promo = p.detail_kode_promo
                    WHERE dtm.id_member = %s AND p.detail_kode_promo LIKE 'DK%%' AND dtm.sisa_kunjungan > 0
                """

                # Only run promo deduction logic if harga_paket_msg == 0 AND id_member is provided
            q_getidmember = "SELECT id_member FROM main_transaksi WHERE id_transaksi = %s"
            await cursor.execute(q_getidmember, (id_trans,))
            id_member = await cursor.fetchone()

            print('idmember :',id_member)
            
            if item['harga_paket_msg'] == 0 and id_member[0] and id_member[0].strip() != "":
                q_check = """
                    SELECT DISTINCT dtm.id_member, dtm.kode_promo, dtm.sisa_kunjungan
                    FROM detail_transaksi_member dtm
                    JOIN promo p ON dtm.kode_promo = p.kode_promo
                    JOIN detail_promo_kunjungan dpk ON dpk.detail_kode_promo = p.detail_kode_promo
                    WHERE dtm.id_member = %s AND p.detail_kode_promo LIKE 'DK%%' AND dtm.sisa_kunjungan > 0 AND p.nama_promo = %s
                """

                await cursor.execute(q_check, (id_member,nama_paket))
                result_check = await cursor.fetchall()
                print("Promo check result:", result_check)

                if result_check:      
                      promo_index = promo_index_store.get("promo_key",0) % len(result_check)
                      id_member_kunjungan = result_check[promo_index][0]
                      kode_promo_kunjungan = result_check[promo_index][1]

                      qty = item['jlh']
                      # qty = promo_qty_map.get(kode_promo_kunjungan)  # quantity to decrement

                      # if qty is None :
                      #   print(f"skipping decrement for member {id_member_kunjungan}, promo {kode_promo_kunjungan}")
                      #   continue

                      print(f"Decrementing sisa_kunjungan by {qty} for member {id_member_kunjungan}, promo {kode_promo_kunjungan}")

                      q_update = """
                          UPDATE detail_transaksi_member
                          SET sisa_kunjungan = CASE
                              WHEN sisa_kunjungan >= %s THEN sisa_kunjungan - %s
                              WHEN sisa_kunjungan > 0 THEN 0
                              ELSE 0
                          END
                          WHERE id_member = %s AND kode_promo = %s;
                      """
                      await cursor.execute(q_update, (qty, qty, id_member_kunjungan, kode_promo_kunjungan))
                promo_index_store["promo_key"] = promo_index + 1
                print("About to commit transaction")
        
          qSelectAddOn = "SELECT total_addon, jenis_pembayaran, disc, pajak FROM main_transaksi WHERE id_transaksi = %s"
          await cursor.execute(qSelectAddOn, (id_trans, ))
          item_main = await cursor.fetchone()
          currentTotalAddOn = 0 if not item_main['total_addon'] else item_main['total_addon']
          jenis_pembayaran_main = item_main['jenis_pembayaran']
          disc_main = item_main['disc']
          pajak_main = item_main['pajak']

          # diskonkan kalo dia payment di akhir. 
          if jenis_pembayaran_main == 1:
            disc_nominal_addon = total_addon * disc_main
            total_addon -= disc_nominal_addon
          # end Diskon

          print(f"Isi Total Addon tambahpaket {total_addon}")

          # kenakan pajak ke addon baru
          # nominal_pjk = total_addon * float(pajak_main)
          # total_addon += nominal_pjk

          q3 = "UPDATE main_transaksi SET total_addon = %s WHERE id_transaksi = %s"
          await cursor.execute(q3, (currentTotalAddOn + total_addon, id_trans))

          # Select Durasi Sementaranya lagi
          q4 = "SELECT sum_durasi_menit FROM durasi_kerja_sementara WHERE id_transaksi = %s"
          await cursor.execute(q4, (id_trans, ))
          items = await cursor.fetchone()
          current_durasi = items['sum_durasi_menit']
          sum_durasi = current_durasi + total_durasi_global

          q5 = "UPDATE durasi_kerja_sementara SET sum_durasi_menit = %s WHERE id_transaksi = %s"
          await cursor.execute(q5, (sum_durasi, id_trans))
                
          await conn.commit()

          qSelectMain = "SELECT * FROM main_transaksi WHERE id_transaksi = %s"
          await cursor.execute(qSelectMain, (id_trans, ))
          item_main = await cursor.fetchone()

          qSelectRuangan = "SELECT nama_ruangan FROM ruangan WHERE id_ruangan = %s"
          await cursor.execute(qSelectRuangan, (item_main['id_ruangan'], ))
          item_ruangan = await cursor.fetchone()

          # Ini utk aktifkan websocket kirim ke admin
          for ws_con in kamar_connection:
            await ws_con.send_text(
              json.dumps({
                "id_transaksi": id_trans,
                "status": "tambah_paket_produk",
                "message": f"Ruangan {item_ruangan['nama_ruangan']} menambah paket / produk"
              })
            )

        except aiomysqlerror as e:
          await conn.rollback()
          return JSONResponse(content={"Error Mysql": str(e)}, status_code=500)
        
        except HTTPException as e:
          await conn.rollback()
          return JSONResponse(content={"Error HTTP": str(e.detail)}, status_code=e.status_code)

  except Exception as e:
    return JSONResponse({"Error Get Menu Fnb": str(e)}, status_code=500)
  

