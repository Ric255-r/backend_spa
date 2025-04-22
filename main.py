from fastapi import Depends, FastAPI, APIRouter, Security, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt import JwtAuthorizationCredentials
from router.routeTest import app as app_test
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
# main_router.include_router(app_transaction)
# main_router.include_router(app_admin)


#masukkan main router ke fastapi app
app.include_router(main_router, prefix="/api")

# bawaan default
if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="192.168.0.112", port=5500)
