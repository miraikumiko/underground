from fastapi import FastAPI, APIRouter, Depends, HTTPException
from src.auth.utils import users
from src.user.models import User
from src.user.schemas import UserCreate, UserRead, UserUpdate
from src.server.schemas import ActiveServerCreate, ActiveServerUpdate
from src.user.crud import (
    crud_add_user,
    crud_get_users,
    crud_get_user,
    crud_update_user,
    crud_update_user_email,
    crud_update_user_password,
    crud_delete_user,
    crud_add_user_server,
    crud_get_user_servers,
    crud_get_user_server,
    crud_update_user_server,
    crud_delete_user_server
)
from src.logger import logger

router = APIRouter(
    prefix="/api/user",
    tags=["user"]
)

active_user = users.current_user(active=True)
active_and_verified_user = users.current_user(active=True, verified=True)
admin = users.current_user(active=True, superuser=True, verified=True)


@router.post("/add")
async def add_user(data: UserCreate, user: User = Depends(admin)):
    try:
        await crud_add_user(data.email, data.password)

        return {
            "status": "success",
            "data": None,
            "details": f"user {data.email} has been added"
        }
    except Exception:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.get("/all")
async def get_users(user: User = Depends(admin)):
    try:
        users = await crud_get_users()

        return {
            "status": "success",
            "data": users,
            "details": "info of all users"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.get("/{id}")
async def get_user(id: int, user: User = Depends(admin)):
    try:
        user = await crud_get_user(id)

        return {
            "status": "success",
            "data": user,
            "details": "user info"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.post("/update/email")
async def update_user_password(email: str, user: User = Depends(active_and_verified_user)):
    try:
        await crud_update_user_email(user.id, email)

        return {
            "status": "success",
            "data": None,
            "details": "email has been changed"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.post("/update/password")
async def update_user_password(password: str, user: User = Depends(active_and_verified_user)):
    try:
        await crud_update_user_password(user.id, password)

        return {
            "status": "success",
            "data": None,
            "details": "password has been changed"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.post("/update/{id}")
async def update_user(id: int, data: UserUpdate, user: User = Depends(admin)):
    try:
        await crud_update_user(id, data)

        return {
            "status": "success",
            "data": None,
            "details": f"user {data.email} has been updated"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.delete("/delete/{id}")
async def delete_user(id: int, user: User = Depends(admin)):
    try:
        await crud_delete_user(id)

        return {
            "status": "success",
            "data": None,
            "details": f"user with id {id} has been deleted"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.post("/server/add")
async def add_user_server(data: ActiveServerCreate, user: User = Depends(admin)):
    try:
        await crud_add_user_server(data)

        return {
            "status": "success",
            "data": None,
            "details": f"server with id {data.server_id} has been added to user with id {data.user_id}"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.get("/server/all")
async def get_user_servers(id: int, user: User = Depends(admin)):
    try:
        servers = await crud_get_user_servers(id)

        return {
            "status": "success",
            "data": servers,
            "details": f"info of all servers of user with id {id}"
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.get("/server/get")
async def get_user_server(user_id: int, server_id: int, user: User = Depends(admin)):
    try:
        server = await crud_get_user_server(user_id, server_id)

        return {
            "status": "success",
            "data": server,
            "details": "user server info"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.post("/server/update")
async def update_user_server(id: int, data: ActiveServerUpdate, user: User = Depends(admin)):
    try:
        await crud_update_user_server(id, data)

        return {
            "status": "success",
            "data": None,
            "details": f"user server with id {id} has been updated"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.delete("/server/delete/{id}")
async def delete_user_server(id: int, user: User = Depends(admin)):
    try:
        await crud_delete_user_server(id)

        return {
            "status": "success",
            "data": None,
            "details": f"user server with id {id} has been deleted"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


def add_user_router(app: FastAPI):
    app.include_router(router)
