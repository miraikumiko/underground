from fastapi import (
    APIRouter,
    UploadFile,
    HTTPException,
    Depends
)
from src.logger import logger
from src.server.crud import (
    crud_create_server,
    crud_read_servers,
    crud_read_server,
    crud_update_server,
    crud_delete_server,
    crud_create_active_server,
    crud_read_active_servers,
    crud_read_active_server,
    crud_update_active_server
)
from src.server.schemas import (
    ServerCreate,
    ServerUpdate,
    ActiveServerCreate,
    ActiveServerUpdate
)
from src.server.vps import (
    vps_on,
    vps_reboot,
    vps_off,
    vps_status
)
from src.server.utils import upload_iso
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
async def read_servers():
    try:
        servers = await crud_read_servers()

        return servers
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/{server_id}")
async def read_server(server_id: int):
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


@router.patch("/update/{server_id}")
async def update_server(server_id: int, data: ServerUpdate, _: User = Depends(admin)):
    try:
        await crud_update_server(data, server_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.delete("/delete/{server_id}")
async def delete_server(server_id: int, _: User = Depends(admin)):
    try:
        await crud_delete_server(server_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.post("/active/create")
async def create_active_server(data: ActiveServerCreate, _: User = Depends(admin)):
    try:
        active_server_id = await crud_create_active_server(data)

        return {"id": active_server_id}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/active/me")
async def read_active_servers(user: User = Depends(active_user)):
    try:
        active_servers = await crud_read_active_servers(user.id)

        return active_servers
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/active/{active_server_id}")
async def read_active_server(active_server_id: int, _: User = Depends(admin)):
    try:
        active_server = await crud_read_active_server(active_server_id)

        return active_server
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.patch("/active/{active_server_id}")
async def update_active_server(active_server_id: int, data: ActiveServerUpdate, _: User = Depends(admin)):
    try:
        await crud_update_active_server(data, active_server_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.post("/active/action/me")
async def server_action(active_server_id: int, action: str, _: User = Depends(active_user)):
    try:
        if action == "on":
            await vps_on(active_server_id)
        elif action == "reboot":
            await vps_reboot(active_server_id)
        elif action == "off":
            await vps_off(active_server_id)
        else:
            raise ValueError("Invalid server action")
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/active/status/{active_server_id}")
async def status_of_server(active_server_id: int, _: User = Depends(active_user)):
    try:
        status = await vps_status(active_server_id)

        return status
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.post("/active/upload/iso")
async def upload_iso_server(iso: UploadFile, user: User = Depends(active_user)):
    try:
        if iso.content_type != "application/octet-stream":
            raise HTTPException(status_code=400, detail="This is not .iso file")

        await upload_iso(user.id, iso)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)
