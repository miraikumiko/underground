from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from src.auth.utils import users
from src.user.models import User
from src.server.models import Server
from src.server.schemas import ServerCreate, ServerUpdate
from src.server.crud import (
    crud_add_server,
    crud_get_servers,
    crud_get_server,
    crud_update_server,
    crud_delete_server
)
from src.logger import logger

router = APIRouter(
    prefix="/api/server",
    tags=["server"]
)

admin = users.current_user(active=True, superuser=True, verified=True)


@router.post("/add")
async def add_server(data: ServerCreate, user: User = Depends(admin)):
    try:
        await crud_add_server(data)

        return {
            "status": "success",
            "data": None,
            "details": "adding server info"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.get("/all")
@cache(expire=3600)
async def get_servers():
    try:
        servers = await crud_get_servers()

        return {
            "status": "success",
            "data": servers,
            "details": "info of all servers"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.get("/{id}")
@cache(expire=3600)
async def get_server(id: int):
    try:
        server = await crud_get_server(id)

        return {
            "status": "success",
            "data": server,
            "details": "server info"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.patch("/update/{id}")
async def update_server(id: int, data: ServerUpdate, user: User = Depends(admin)):
    try:
        await crud_update_server(id, data)

        return {
            "status": "success",
            "data": None,
            "details": f"server with id {id} has been updated"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


@router.delete("/delete/{id}")
async def delete_server(id: int, user: User = Depends(admin)):
    try:
        await crud_delete_server(id)

        return {
            "status": "success",
            "data": None,
            "details": f"server with id {id} has been deleted"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "server error"
        })


def add_server_router(app: FastAPI):
    app.include_router(router)
