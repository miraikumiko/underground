import base64
from uuid import uuid4
from random import choice, randint
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from captcha.image import ImageCaptcha
from src.database import r
from src.config import PRODUCTS
from src.user.models import User
from src.auth.utils import active_user, auth_check
from src.payment.utils import xmr_course, draw_qrcode

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def index(request: Request, is_authorized: User = Depends(auth_check)):
    course = await xmr_course()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": is_authorized,
        "course": course,
        "products": PRODUCTS["vps"]
    })


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register(request: Request):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    text = ''.join(choice(chars) for _ in range(randint(5, 7)))
    captcha_id = randint(10000000, 99999999)

    image = ImageCaptcha(width=218, height=50)
    captcha = base64.b64encode(image.generate(text).getvalue()).decode("utf-8")

    await r.set(f"captcha:{captcha_id}", text, ex=90)

    return templates.TemplateResponse("register.html", {
        "request": request, "captcha_id": captcha_id, "captcha": captcha
    })


@router.get("/reset-password")
async def change_password(request: Request, is_authorized: User = Depends(active_user)):
    return templates.TemplateResponse("change-password.html", {"request": request})


@router.get("/delete-account")
async def delete_account(request: Request, is_authorized: User = Depends(active_user)):
    return templates.TemplateResponse("delete-account.html", {"request": request})


@router.post("/logout")
async def logout(_: User = Depends(active_user)):
    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure'
    })


@router.get("/checkout/{product_id}")
async def checkout(request: Request, is_authorized: User = Depends(active_user)):
    uri = "monero://aaaaa"
    qrcode = await draw_qrcode(uri)

    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "qrcode": qrcode,
        "uri": uri,
        "ttl": 900
    })
