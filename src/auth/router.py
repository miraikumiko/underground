from uuid import uuid4
from random import choice, randint
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, JSONResponse, StreamingResponse
from captcha.image import ImageCaptcha
from src.database import r
from src.crud import crud_read
from src.logger import logger
from src.auth.schemas import Login, Register, Captcha, ResetPassword
from src.auth.utils import password_helper, active_user
from src.user.models import User
from src.user.schemas import UserCreate, UserUpdate
from src.user.crud import crud_create_user, crud_update_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(data: Login):
    user = await crud_read(User, attr1=User.username, attr2=data.username)

    if user is None:
        raise HTTPException(status_code=400, detail="User doesn't exist")

    if password_helper.verify_and_update(data.password, user.password)[0]:
        token = uuid4()
        await r.set(f"auth:{token}", user.id, ex=86400)

        return Response(status_code=204, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Secure; Max-Age=86400"
        })
    else:
        raise HTTPException(status_code=401, detail="Invalid password")


@router.post("/register")
async def register(data: Register):
    captcha = await r.get(f"captcha:{data.captcha_id}")
    await r.delete(f"captcha:{data.captcha_id}")

    if captcha is None:
        raise HTTPException(status_code=400, detail="Captcha was expired")

    if captcha != data.captcha_text:
        raise HTTPException(status_code=400, detail="Captcha didn't match")

    if len(data.username) not in range(21):
        raise HTTPException(
            status_code=400, detail="Username must be up to 20 characters"
        )

    if not data.username.isalnum():
        raise HTTPException(
            status_code=400,
            detail="Username must be contain only letters and numbers"
        )

    if len(data.password) not in range(51):
        raise HTTPException(
            status_code=400, detail="Password must be up to 50 characters"
        )

    user = await crud_read(User, attr1=User.username, attr2=data.username)

    if user is None:
        user = UserCreate(
            username=data.username, password=password_helper.hash(data.password)
        )
        user_id = await crud_create_user(user)

        return JSONResponse({"user_id": user_id}, status_code=201)
    else:
        raise HTTPException(status_code=400, detail="User already exist")


@router.get("/captcha")
async def get_captcha():
    try:
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        text = ''.join(choice(chars) for _ in range(randint(5, 7)))
        captcha_id = randint(10000000, 99999999)

        image = ImageCaptcha(width=218, height=50)
        captcha = image.generate(text)

        await r.set(f"captcha:{captcha_id}", text, ex=180)

        return StreamingResponse(captcha, headers={"captcha_id": str(captcha_id)}, media_type="image/png")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.post("/logout")
async def logout(_: User = Depends(active_user)):
    try:
        return Response(status_code=204, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure'
        })
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.post("/reset-password")
async def reset_password(data: ResetPassword, user: User = Depends(active_user)):
    try:
        if password_helper.verify_and_update(data.old_password, user.password)[0]:
            schema = UserUpdate()
            schema.password = password_helper.hash(data.new_password)

            await crud_update_user(schema, user.id)

            return Response(status_code=204)
        else:
            return Response(status_code=401)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)
