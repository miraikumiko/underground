from fastapi import APIRouter, UploadFile, HTTPException, Depends
from src.logger import logger
from src.server.crud import (
    crud_create_server,
    crud_read_servers,
    crud_read_server,
    crud_update_server,
    crud_delete_server
)
from src.server.schemas import ServerCreate, ServerUpdate, VPSInstall
from src.server.vps import vps_create, vps_action, vps_status
from src.user.models import User
from src.auth.utils import active_user, admin

router = APIRouter(prefix="/api/server", tags=["servers"])


@router.post("/create")
async def create_server(data: ServerCreate, _: User = Depends(admin)):
    try:
        server_id = await crud_create_server(data)

        return {"id": server_id}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/all")
async def read_servers(_: User = Depends(admin)):
    try:
        servers = await crud_read_servers()

        return servers
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/me")
async def read_my_servers(user: User = Depends(active_user)):
    try:
        servers = await crud_read_servers(user.id)

        return servers
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/{server_id}")
async def read_server(server_id: int, _: User = Depends(admin)):
    try:
        server = await crud_read_server(server_id)

        if server is None:
            raise ValueError(f"Server with id {server_id} doesn't exist")

        return server
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.patch("/{server_id}")
async def update_server(server_id: int, data: ServerUpdate, _: User = Depends(admin)):
    try:
        await crud_update_server(data, server_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.delete("/{server_id}")
async def delete_server(server_id: int, _: User = Depends(admin)):
    try:
        await crud_delete_server(server_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.post("/install/{server_id}")
async def action(data: VPSInstall, server_id: int, user: User = Depends(active_user)):
    server = await crud_read_server(server_id)

    if server is None:
        raise HTTPException(status_code=400)
    elif not server.active:
        raise HTTPException(status_code=400, detail=f"Server {server_id} is not active")
    elif server.user_id != user.id or not user.is_superuser:
        raise HTTPException(status_code=400)

    try:
        await vps_create(server_id, data.os)
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action")
async def action(server_id: int, cmd: str, user: User = Depends(active_user)):
    try:
        server = await crud_read_server(server_id)

        if server is None:
            raise HTTPException(status_code=400)
        elif not server.active:
            raise HTTPException(status_code=400, detail=f"Server {server_id} is not active")
        elif server.user_id != user.id or not user.is_superuser:
            raise HTTPException(status_code=400)

        if cmd in ("on", "reboot", "off", "delete"):
            await vps_action(server_id, cmd)
        else:
            raise ValueError("Invalid server action")
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/status/{server_id}")
async def status(server_id: int, user: User = Depends(active_user)):
    try:
        server = await crud_read_server(server_id)

        if server is None:
            raise HTTPException(status_code=400)
        elif not server.active:
            raise HTTPException(status_code=400)
        elif server.user_id != user.id or not user.is_superuser:
            raise HTTPException(status_code=400)

        stat = await vps_status(server_id)

        return stat
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)
