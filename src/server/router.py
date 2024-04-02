from fastapi import APIRouter, UploadFile, HTTPException, Depends
from src.logger import logger
from src.server.crud import (
    crud_create_server,
    crud_read_servers,
    crud_read_server,
    crud_update_server,
    crud_delete_server
)
from src.server.schemas import ServerCreate, ServerUpdate
from src.server.vps import vps_action, vps_status
from src.server.utils import upload_iso
from src.user.models import User
from src.auth.utils import active_user, admin

router = APIRouter(prefix="/api/server", tags=["servers"])


@router.post("")
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


@router.post("/action/me")
async def action(server_id: int, command: str, user: User = Depends(active_user)):
    try:
        server = await crud_read_server(server_id)

        if server is None:
            raise HTTPException(status_code=400)

        if server.user_id != user.id:
            raise HTTPException(status_code=400)

        if command == "on":
            await vps_action(server_id, command)
        elif command == "reboot":
            await vps_action(server_id, command)
        elif command == "off":
            await vps_action(server_id, command)
        else:
            raise ValueError("Invalid server action")
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/status/{server_id}")
async def status(server_id: int, _: User = Depends(active_user)):
    try:
        stat = await vps_status(server_id)

        return stat
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.post("/upload/iso")
async def upload_iso(iso: UploadFile, user: User = Depends(active_user)):
    try:
        if iso.content_type != "application/octet-stream":
            raise HTTPException(status_code=400, detail="This is not .iso file")

        await upload_iso(user.id, iso)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)
