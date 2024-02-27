from fastapi import (
    APIRouter,
    UploadFile,
    HTTPException,
    Depends
)
from fastapi_cache.decorator import cache
from src.logger import logger
from src.server.crud import (
    crud_add_server,
    crud_get_servers,
    crud_get_server,
    crud_update_server,
    crud_delete_server,
    crud_add_active_server,
    crud_get_active_servers,
    crud_get_active_server,
    crud_update_active_server
)
from src.server.schemas import (
    ServerCreate,
    ServerUpdate,
    ActiveServerCreate,
    ActiveServerUpdate,
    ActiveServerAction
)
from src.server.vps import (
    vps_server_on,
    vps_server_reboot,
    vps_server_off,
    vps_server_status
)
from src.server.utils import upload_iso
from src.user.models import User
from src.auth.utils import active_user, admin

router = APIRouter(
    prefix="/api/server",
    tags=["servers"]
)


@router.post("/add")
async def add_server(data: ServerCreate, user: User = Depends(admin)):
    try:
        await crud_add_server(data)

        return {
            "status": "success",
            "data": None,
            "details": "Server info has been added"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.get("/all")
@cache(expire=3600)
async def get_servers():
    try:
        servers = await crud_get_servers()

        return {
            "status": "success",
            "data": servers,
            "details": "Info of all servers"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.get("/{id}")
@cache(expire=3600)
async def get_server(id: int):
    try:
        server = await crud_get_server(id)

        if server is None:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "data": None,
                "details": "Server doesn't exist"
            })

        return {
            "status": "success",
            "data": server,
            "details": "Server info"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.post("/update/{id}")
async def update_server(id: int, data: ServerUpdate, user: User = Depends(admin)):
    try:
        await crud_update_server(id, data)

        return {
            "status": "success",
            "data": None,
            "details": f"Server with id {id} has been updated"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.delete("/delete/{id}")
async def delete_server(id: int, user: User = Depends(admin)):
    try:
        await crud_delete_server(id)

        return {
            "status": "success",
            "data": None,
            "details": f"Server with id {id} has been deleted"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.post("/active/add")
async def add_active_server(data: ActiveServerCreate, user: User = Depends(active_user)):
    try:
        await crud_add_active_server(data)

        return {
            "status": "success",
            "data": None,
            "details": "Active server has been added"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.get("/active/me")
async def get_active_servers(user: User = Depends(active_user)):
    try:
        servers = await crud_get_active_servers(user.id)

        return {
            "status": "success",
            "data": servers,
            "details": f"Info of all servers of user with id {user.id}"
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.get("/active/me/{id}")
async def get_active_server(id: int, user: User = Depends(active_user)):
    try:
        server = await crud_get_active_server(id)

        return {
            "status": "success",
            "data": server,
            "details": "User server info"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.patch("/active/me/{id}")
async def update_active_server(data: ActiveServerUpdate, user: User = Depends(active_user)):
    try:
        await crud_update_active_server(data)

        return {
            "status": "success",
            "data": None,
            "details": f"User server with id {id} has been updated"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.post("/active/action")
async def action_of_server(data: ActiveServerAction, user: User = Depends(active_user)):
    try:
        if data.action == "on":
            await vps_server_on(str(data.active_server_id))
        elif data.action == "reboot":
            await vps_server_reboot(str(data.active_server_id))
        elif data.action == "off":
            await vps_server_off(str(data.active_server_id))
        else:
            raise ValueError("Invalid server action")

        return {
            "status": "success",
            "data": None,
            "details": f"Server has been {data.action}"
        }
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "data": None,
            "details": e
        })
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.get("/active/status/{active_server_id}")
async def status_of_server(active_server_id: int, user: User = Depends(active_user)):
    try:
        status = await vps_server_status(active_server_id)

        return {
            "status": "success",
            "data": status,
            "details": "Server info"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })


@router.post("/active/upload/iso")
async def upload_iso_server(server_id: int, iso: UploadFile, user: User = Depends(active_user)):
    if iso.content_type != "application/octet-stream":
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "data": None,
            "details": "This is not .iso file"
        })
    try:
        await upload_iso(user.id, iso)

        return {
            "status": "success",
            "data": None,
            "details": "Image has been uploaded"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })
