from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.config import BASE_PATH
from src.auth.router import router as auth_router
from src.payment.router import router as payment_router
from src.server.router import router as server_router
from src.display.router import router as display_router
from src.display.utils import t_error


app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory=f"{BASE_PATH}/static"), name="static")
app.include_router(auth_router)
app.include_router(payment_router)
app.include_router(server_router)
app.include_router(display_router)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail.split('|')

    if detail[0] == 'd':
        return await t_error(request, exc.status_code, detail[1])
