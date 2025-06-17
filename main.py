import os
from fastapi import Depends, FastAPI, APIRouter, Security, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_jwt import JwtAuthorizationCredentials
from router.routeTest import app as app_test
from router.user.login import app as app_login
from router.transaksi.fnb import app as app_fnb
from router.admin.regis_kamar import app as app_room
from router.admin.regis_pekerja import app as app_pekerja
from router.admin.daftarfnb import app as app_daftarfnb
from router.admin.daftarpaketmassage import app as app_daftarpaketmassage
from router.admin.daftarproduk import app as app_daftarproduk
from router.admin.daftarfasilitas import app as app_daftarfasilitas
from router.admin.daftarpromo import app as app_daftarpromo
from router.admin.listpaketmassage import app as app_listpaketmassage
from router.admin.listpaketfnb import app as app_listfnb
from router.admin.regis_users import app as app_regisusers
from router.admin.list_pekerja import app as app_listpekerja
from router.admin.list_room import app as app_listroom
from router.admin.laporan_ob import app as app_laporanob
from router.admin.list_transaksi import app as app_listtransaksi
from router.admin.daftarproduk import app as app_daftarproduk
from router.transaksi.kitchen import app as app_kitchen
from router.admin.listproduk import app as app_listproduk
from router.admin.listfasilitas import app as app_listfasilitas
from router.admin.selectsearchfood import app as app_selectsearchfood
from router.admin.listpromo import app as app_listpromo
from router.admin.daftarlocker import app as app_daftarlocker
from router.admin.selectsearchpromo import app as app_selectsearchpromo
from router.terapis.billinglocker import app as app_billinglocker
from router.transaksi.kitchen import app as app_kitchen
from router.ob.start_kerja import app as app_ob
from router.transaksi.kitchen import app as app_kitchen
from router.terapis.kamar_terapis import app as app_kamarterapis
from router.admin.list_user import app as app_datauser
from router.transaksi.massages import app as app_transaksimassage
from router.transaksi.draft_idtrans import app as app_idtrans
from router.terapis.extend_time import app as app_extends
from router.spv.terima_panggilan import app as app_terimapanggilan
from router.resepsionis.room import app as app_ruangan
from router.admin.absensi_terapis import app as app_absensi_terapis
from router.transaksi.fasilitas import app as app_fasilitas
from router.transaksi.regis_member import app as app_regis_member
from router.admin.list_member import app as app_listmember
from router.terapis.revisi_data import app as app_revisiservice
from router.terapis.savekomisi import app as app_savekomisi
from router.transaksi.member import app as app_transmember
from router.owner.main_owner import app as app_owner
from router.resepsionis.history_member import app as app_historymember
from router.komisi.komisi import app as app_komisi
from router.admin.pajak import app as app_pajak
from router.admin.daftarpaketextend import app as app_daftarpaketextend
from jwt_auth import access_security

from koneksi import lifespan
IMAGEDIR = "assets/ob"
if not os.path.exists(IMAGEDIR):
    os.makedirs(IMAGEDIR)
app = FastAPI(lifespan=lifespan)
app.mount("/api/images", StaticFiles(directory=IMAGEDIR), name="images")

KONTRAK_DIR = "kontrak"
os.makedirs(KONTRAK_DIR, exist_ok=True)
app.mount("/listpekerja/kontrak", StaticFiles(directory=KONTRAK_DIR), name="kontrak")

app.mount("/qrcodes", StaticFiles(directory="qrcodes"), name="qrcodes")
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)



main_router = APIRouter()

main_router.include_router(app_test)
main_router.include_router(app_login)
main_router.include_router(app_fnb)
main_router.include_router(app_room)
main_router.include_router(app_pekerja)
main_router.include_router(app_daftarfnb)
main_router.include_router(app_daftarpaketmassage)
main_router.include_router(app_regisusers)
main_router.include_router(app_listpekerja)
main_router.include_router(app_listroom)
main_router.include_router(app_daftarproduk)
main_router.include_router(app_kitchen)
main_router.include_router(app_daftarfasilitas)
main_router.include_router(app_daftarpromo)
main_router.include_router(app_listpaketmassage)
main_router.include_router(app_listfnb)
main_router.include_router(app_laporanob)
main_router.include_router(app_kitchen)
main_router.include_router(app_listtransaksi)
main_router.include_router(app_ob)
main_router.include_router(app_kamarterapis)
main_router.include_router(app_datauser)
main_router.include_router(app_listproduk)
main_router.include_router(app_transaksimassage)
main_router.include_router(app_idtrans)
main_router.include_router(app_listfasilitas)
main_router.include_router(app_selectsearchfood)
main_router.include_router(app_listpromo)
main_router.include_router(app_selectsearchpromo)
main_router.include_router(app_daftarlocker)
main_router.include_router(app_billinglocker)
main_router.include_router(app_extends)
main_router.include_router(app_terimapanggilan)
main_router.include_router(app_ruangan )
main_router.include_router(app_absensi_terapis)
main_router.include_router(app_fasilitas)
main_router.include_router(app_regis_member)
main_router.include_router(app_listmember)
main_router.include_router(app_revisiservice)
main_router.include_router(app_savekomisi)
main_router.include_router(app_transmember)
main_router.include_router(app_owner)
main_router.include_router(app_historymember)
main_router.include_router(app_komisi)
main_router.include_router(app_pajak)
main_router.include_router(app_daftarpaketextend)
# main_router.include_router(app_transaction)
# main_router.include_router(app_admin)


#masukkan main router ke fastapi app
app.include_router(main_router, prefix="/api")

# bawaan default
if __name__ == "__main__":
  import uvicorn
  # Cara jalanin dgn Reload
  # uvicorn main:app --reload --host 192.168.100.11 --port 5500
  uvicorn.run(app, host="192.168.100.11", port=5500)
