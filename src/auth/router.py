from uuid import uuid4
from random import choice, randint
from pydantic import EmailStr
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import (
    Response,
    JSONResponse,
    StreamingResponse,
    RedirectResponse
)
from captcha.image import ImageCaptcha
from src.database import r
from src.crud import crud_read
from src.mail import sendmail
from src.config import SERVICE_NAME, DOMAIN, ONION_DOMAIN, I2P_DOMAIN
from src.logger import logger
from src.auth.schemas import (
    Login,
    Register,
    ResetPassword,
    ResetEmail,
    Recovery,
    Captcha
)
from src.auth.utils import active_user
from src.auth.password import password_helper
from src.user.models import User
from src.user.schemas import (
    UserCreate,
    UserUpdate,
    UserSettingsCreate,
    UserSettingsUpdate
)
from src.user.crud import (
    crud_create_user,
    crud_update_user,
    crud_create_user_settings,
    crud_read_user_settings,
    crud_update_user_settings
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(data: Login):
    user = await crud_read(User, attr1=User.username, attr2=data.username)

    if user is None:
        raise HTTPException(status_code=400, detail="User doesn't exist")

    if password_helper.verify_and_update(data.password, user.hashed_password)[0]:
        token = uuid4()
        await r.set(f"auth:{token}", user.id, ex=604800)

        return Response(status_code=204, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Secure; Max-Age=604800"
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

    user = await crud_read(User, attr1=User.username, attr2=data.username)

    if user is None:
        user = UserCreate(username=data.username, password=data.password)
        user_id = await crud_create_user(user)

        user_settings = UserSettingsCreate(user_id=user_id)
        await crud_create_user_settings(user_settings)

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
        if password_helper.verify_and_update(data.old_password, user.hashed_password)[0]:
            schema = UserUpdate()
            schema.password = data.new_password

            await crud_update_user(schema, user.id)

            return Response(status_code=204)
        else:
            return Response(status_code=401)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.post("/reset-email")
async def reset_email(data: ResetEmail, user: User = Depends(active_user)):
    try:
        schema = UserUpdate()
        schema.email = data.email
        schema.is_verified = False

        await crud_update_user(schema, user.id)

        token = uuid4()

        await r.set(f"verify:{token}", user.id, ex=(60 * 60 * 24))

        subject = f"[{SERVICE_NAME}] verification"
        body = f"""
Verify your email:
https://{DOMAIN}/api/auth/verify/{token}
http://{ONION_DOMAIN}/api/auth/verify/{token}
http://{I2P_DOMAIN}/api/auth/verify/{token}

Links expire within 24 hours.
If you received this letter by mistake, please write to the administrator: admin@{DOMAIN}
        """

        await sendmail(subject, body, data.email)

        return Response(status_code=204)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.post("/verify/{token}")
async def verify(token: str):
    try:
        user_id = await r.get(f"verify:{token}")

        if user_id is None:
            raise HTTPException(status_code=400)

        UserSchema = UserUpdate()
        UserSchema.is_verified = True

        SettingsSchema = UserSettingsUpdate()
        SettingsSchema.notifications = True
        SettingsSchema.reset_password = True

        await crud_update_user(UserSchema, int(user_id))
        await crud_update_user_settings(SettingsSchema, int(user_id))
        await r.delete(token)

        return RedirectResponse('/')
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.post("/recovery")
async def recovery(data: Recovery):
    try:
        user = await crud_read(User, attr1=User.username, attr2=data.username)

        if user is None:
            return Response(status_code=401)

        if not user.is_verified or user.email != data.email:
            return Response(status_code=401)

        user_settings = await crud_read_user_settings(user.id)

        if not user_settings.reset_password:
            return Response(status_code=401)

        password = str(uuid4())

        schema = UserUpdate()
        schema.password = password

        await crud_update_user(schema, user.id)

        subject = f"[{SERVICE_NAME}] recovery"
        body = f"""
Your new password is: {password}

If you received this letter by mistake, please write to the administrator: admin@{DOMAIN}
        """

        await sendmail(subject, body, data.email)

        return Response(status_code=204)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)
