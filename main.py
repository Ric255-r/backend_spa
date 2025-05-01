from fastapi import Depends, FastAPI, APIRouter, Security, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt import JwtAuthorizationCredentials
from router.routeTest import app as app_test
from router.user.login import app as app_login
from router.transaksi.fnb import app as app_fnb
from router.admin.regis_produk import app as app_produk
from router.admin.regis_kamar import app as app_room
from router.admin.regis_pekerja import app as app_pekerja
from router.admin.daftarfnb import app as app_daftarfnb
from router.admin.daftarpaketmassage import app as app_daftarpaketmassage
from router.admin.regis_users import app as app_regisusers
from router.admin.list_pekerja import app as app_listpekerja
from router.admin.list_room import app as app_listroom
# from router.transaksi.fnb import app 
from jwt_auth import access_security

from koneksi import lifespan

app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

main_router = APIRouter()

main_router.include_router(app_test)
main_router.include_router(app_login)
main_router.include_router(app_fnb)
main_router.include_router(app_produk)
main_router.include_router(app_room)
main_router.include_router(app_pekerja)
main_router.include_router(app_daftarfnb)
main_router.include_router(app_daftarpaketmassage)
main_router.include_router(app_regisusers)
main_router.include_router(app_listpekerja)
main_router.include_router(app_listroom)
# main_router.include_router(app_fnb)
# main_router.include_router(app_transaction)
# main_router.include_router(app_admin)


#masukkan main router ke fastapi app
app.include_router(main_router, prefix="/api")

# bawaan default
if __name__ == "__main__":
  import uvicorn
  # Cara jalanin dgn Reload
  # uvicorn main:app --reload --host 192.168.100.11 --port 5500
  uvicorn.run(app, host="10.10.10.228", port=5500)
