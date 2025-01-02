import base64
from io import BytesIO
from datetime import datetime
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_L
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from src.config import BASE_PATH

templates = Jinja2Templates(directory=f"{BASE_PATH}/templates")
templates.env.filters["to_days"] = lambda date: (datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()).days

no_cache_headers = {
    "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}


async def template_error(request: Request, status_code: int, detail: str):
    return templates.TemplateResponse(request, "error.html", {
        "status_code": status_code,
        "detail": detail
    }, status_code=status_code)


async def draw_qrcode(text: str) -> str:
    qr = QRCode(version=1, error_correction=ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(text)
    qr.make()
    img = qr.make_image()
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    qrcode = base64.b64encode(img_bytes.getvalue()).decode("utf-8")

    return qrcode
