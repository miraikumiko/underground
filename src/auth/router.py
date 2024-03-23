from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import EmailStr
from uuid import uuid4
from src.database import r
from src.crud import crud_read
from src.mail import sendmail
from src.config import SERVICE_NAME, DOMAIN, ONION_DOMAIN, I2P_DOMAIN
from src.logger import logger
from src.user.models import User
from src.user.schemas import UserCreate, UserUpdate, UserSettingsCreate
from src.user.crud import (
    crud_create_user,
    crud_update_user,
    crud_create_user_settings,
    crud_read_user_settings
)
from src.auth.utils import active_user
from src.auth.password import password_helper

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(username: str, password: str):
    try:
        user = await crud_read(User, attr1=User.username, attr2=username)

        if password_helper.verify_and_update(password, user.hashed_password)[0]:
            token = uuid4()
            await r.set(f"auth:{token}", user.id, ex=(60 * 60 * 24 * 7))

            return Response(status_code=204, headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Secure"
            })
        else:
            raise HTTPException(status_code=400, detail="Invalid password")
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


@router.post("/register")
async def register(data: UserCreate):
    try:
        user = await crud_read(User, attr1=User.username, attr2=data.username)

        if user is not None:
            user_id = await crud_create_user(data)
            user_settings = UserSettingsCreate(user_id=user_id)
            await crud_create_user_settings(user_settings)

            return Response({"user_id": user_id}, status_code=201)
        else:
            return Response({"detail": "User exist"}, status_code=400)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.post("/reset-password")
async def reset_password(old_password: str, new_password: str, user: User = Depends(active_user)):
    try:
        if password_helper.verify_and_update(old_password, user.hashed_password)[0]:
            schema = UserUpdate()
            schema.password = new_password

            await crud_update_user(schema, user.id)

            return Response(status_code=204)
        else:
            return Response(status_code=401)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.post("/reset-email")
async def reset_email(email: EmailStr, user: User = Depends(active_user)):
    try:
        schema = UserUpdate()
        schema.email = email
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

        await sendmail(subject, body, email)

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

        schema = UserUpdate()
        schema.is_verified = True

        await crud_update_user(schema, int(user_id))
        await r.delete(token)

        return Response(status_code=204)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.post("/recovery")
async def recovery(username: str, email: str):
    try:
        user = await crud_read(User, attr1=User.username, attr2=username)

        if user is None:
            return Response(status_code=401)

        if not user.is_verified or user.email != email:
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

        await sendmail(subject, body, email)

        return Response(status_code=204)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)
