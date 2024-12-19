import base64
from io import BytesIO
from random import choice, randint
from captcha.image import ImageCaptcha
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_L
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from src.database import r
from src.config import BASE_PATH
from src.display.filters import to_days, to_minutes

templates = Jinja2Templates(directory=f"{BASE_PATH}/templates")
templates.env.filters["to_days"] = to_days
templates.env.filters["to_minutes"] = to_minutes


async def t_error(request: Request, status_code: int, detail: str) -> templates.TemplateResponse:
    return templates.TemplateResponse("error.html", {
        "request": request,
        "status_code": status_code,
        "detail": detail
    }, status_code=status_code)


async def t_checkout(request: Request, qrcode: str, uri: str, ttl: int) -> templates.TemplateResponse:
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "qrcode": qrcode,
        "uri": uri,
        "ttl": ttl
    })


async def get_captcha_base64() -> [int, str]:
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    text = ''.join(choice(chars) for _ in range(randint(5, 7)))
    captcha_id = randint(10000000, 99999999)

    image = ImageCaptcha(width=218, height=50)
    captcha_base64 = base64.b64encode(image.generate(text).getvalue()).decode("utf-8")

    await r.set(f"captcha:{captcha_id}", text, ex=90)

    return captcha_id, captcha_base64


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
