from fastapi import (
    APIRouter,
    UploadFile,
    HTTPException,
    Depends
)
from fastapi_cache.decorator import cache
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
    ServerRead,
    ServerUpdate,
    ActiveServerCreate,
    ActiveServerRead,
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


@router.post("/create")
async def create_server(Schema: ServerCreate, user: User = Depends(admin)):
    try:
        id = await crud_create_server(Schema)

        return {
            "status": "success",
            "data": {"id": id},
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
async def read_servers():
    try:
        servers = await crud_read_servers()

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
async def read_server(Schema: ServerRead):
    try:
        server = await crud_read_server({"id": Schema.id})

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
async def update_server(Schema: ServerUpdate, user: User = Depends(admin)):
    try:
        await crud_update_server(Schema)

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
        await crud_delete_server({"id": id})

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


@router.post("/active/create")
async def create_active_server(Schema: ActiveServerCreate, user: User = Depends(active_user)):
    try:
        id = await crud_create_active_server(Schema)

        return {
            "status": "success",
            "data": {"id": id},
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
async def read_active_servers(user: User = Depends(active_user)):
    try:
        servers = await crud_read_active_servers({"user_id": user.id})

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


@router.get("/active/{id}")
async def read_active_server(id: int, user: User = Depends(active_user)):
    try:
        server = await crud_read_active_server({"id": id})

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


@router.patch("/active/{id}")
async def update_active_server(Schema: ActiveServerUpdate, user: User = Depends(active_user)):
    try:
        await crud_update_active_server(Schema)

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
async def server_action(Schema: ActiveServerAction, user: User = Depends(active_user)):
    try:
        if Schema.action == "on":
            await vps_server_on(str(Schema.active_server_id))
        elif Schema.action == "reboot":
            await vps_server_reboot(str(Schema.active_server_id))
        elif Schema.action == "off":
            await vps_server_off(str(Schema.active_server_id))
        else:
            raise ValueError("Invalid server action")

        return {
            "status": "success",
            "data": None,
            "details": f"Server has been {Schema.action}"
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
async def upload_iso_server(iso: UploadFile, user: User = Depends(active_user)):
    try:
        if iso.content_type != "application/octet-stream":
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "data": None,
                "details": "This is not .iso file"
            })

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
