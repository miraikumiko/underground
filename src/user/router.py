from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from src.logger import logger
from src.user.models import User
from src.user.schemas import UserUpdate, UserDelete, UserSettingsUpdate
from src.user.crud import (
    crud_read_user,
    crud_update_user,
    crud_delete_user,
    crud_read_user_settings,
    crud_update_user_settings,
    crud_delete_user_settings
)
from src.server.crud import crud_delete_servers
from src.auth.utils import active_user, admin
from src.auth.password import password_helper

router = APIRouter(prefix="/api/user", tags=["users"])


@router.get("/me")
async def read_me(user: User = Depends(active_user)):
    try:
        del user.hashed_password

        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.patch("/me")
async def update_me(data: UserUpdate, user: User = Depends(active_user)):
    try:
        await crud_update_user(data, user.id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.delete("/me")
async def delete_me(data: UserDelete, user: User = Depends(active_user)):
    if password_helper.verify_and_update(data.password, user.hashed_password)[0]:
        await crud_delete_servers(user.id)
        await crud_delete_user_settings(user.id)
        await crud_delete_user(user.id)

        return Response(status_code=204, headers={
            "content-type": "application/x-www-form-urlencoded",
            "set-cookie": 'fastapiusersauth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure'
        })
    else:
        raise HTTPException(status_code=401)


@router.get("/{user_id}")
async def read_user(user_id: int, _: User = Depends(admin)):
    try:
        user = await crud_read_user(user_id)

        if user is None:
            return Response(status_code=404)

        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.patch("/{user_id}")
async def update_user(user_id: int, data: UserUpdate, _: User = Depends(admin)):
    try:
        await crud_update_user(data, user_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.delete("/{user_id}")
async def delete_user(user_id: int, _: User = Depends(admin)):
    try:
        await crud_delete_servers(user_id)
        await crud_delete_user_settings(user_id)
        await crud_delete_user(user_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.get("/settings/me")
async def read_my_settings(user: User = Depends(active_user)):
    try:
        user_settings = await crud_read_user_settings(user.id)

        return user_settings
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)


@router.patch("/settings/me")
async def update_my_settings(data: UserSettingsUpdate, user: User = Depends(active_user)):
    try:
        await crud_update_user_settings(data, user.id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)
