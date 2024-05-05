import socket
import asyncio
from fastapi import APIRouter, WebSocket, Depends, HTTPException
from websockets.exceptions import ConnectionClosedOK
from src.database import r
from src.logger import logger
from src.server.schemas import ServerCreate, ServerUpdate, VPSInstall, VPSAction
from src.server.crud import (
    crud_create_server,
    crud_read_servers,
    crud_read_server,
    crud_update_server,
    crud_delete_server
)
from src.server.vps import vps_install, vps_action, vps_status
from src.node.crud import crud_read_node
from src.user.models import User
from src.user.crud import crud_read_user
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


@router.post("/install")
async def install(data: VPSInstall, user: User = Depends(active_user)):
    server = await crud_read_server(data.server_id)

    if server is None:
        raise HTTPException(status_code=400, detail="Server doesn't exist")
    elif server.user_id != user.id or not user.is_superuser:
        raise HTTPException(status_code=401, detail="Permision denied")
    elif not server.active:
        raise HTTPException(status_code=400, detail="Server is not active")

    try:
        await vps_install(server, data.os)
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action")
async def action(data: VPSAction, user: User = Depends(active_user)):
    try:
        server = await crud_read_server(data.server_id)

        if server is None:
            raise HTTPException(status_code=400)
        elif not server.active:
            raise HTTPException(status_code=400, detail=f"Server {data.server_id} is not active")
        elif server.user_id != user.id or not user.is_superuser:
            raise HTTPException(status_code=400)

        if data.cmd in ("on", "reboot", "off", "delete"):
            await vps_action(data.server_id, data.cmd)
        else:
            raise ValueError("Invalid server action")
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail=str(e))


@router.websocket("/status/{server_id}")
async def status(server_id: int, ws: WebSocket):
    # Check cookie
    has_cookie = "auth" in ws.cookies
    auth_token = ws.cookies["auth"] if has_cookie else None

    if not has_cookie or auth_token is None:
        raise HTTPException(status_code=401)

    user_id = await r.get(f"auth:{auth_token}")
    user = await crud_read_user(int(user_id))

    if user is None or not user.is_active:
        raise HTTPException(status_code=401)

    # Status logic
    server = await crud_read_server(server_id)

    if server is None or not server.active:
        raise HTTPException(status_code=400)
    elif server.user_id != user.id or not user.is_superuser:
        raise HTTPException(status_code=401, detail="Permision denied")

    await ws.accept()

    while True:
        try:
            stat = await vps_status(server_id)
            await ws.send_text(stat)
            await asyncio.sleep(10)
        except ConnectionClosedOK:
            break
        except Exception as e:
            logger.error(e)
            break


@router.websocket("/vnc/{server_id}")
async def vnc(server_id: int, ws: WebSocket):
    # Check cookie
    has_cookie = "auth" in ws.cookies
    auth_token = ws.cookies["auth"] if has_cookie else None

    if not has_cookie or auth_token is None:
        raise HTTPException(status_code=401)

    user_id = await r.get(f"auth:{auth_token}")
    user = await crud_read_user(int(user_id))

    if user is None or not user.is_active:
        raise HTTPException(status_code=401)

    # VNC logic
    server = await crud_read_server(server_id)

    if server is None or not server.active:
        raise HTTPException(status_code=400, detail="Server doesn't exist")
    elif server.user_id != user.id or not user.is_superuser:
        raise HTTPException(status_code=401, detail="Permision denied")

    await ws.accept()

    node = await crud_read_node(server.node_id)

    try:
        reader, writer = await asyncio.open_connection(node.ip, server.vnc_port)
    except ConnectionRefusedError:
        return await ws.close(1013, "VNC Server isn't running now")


    async def read_from_vnc():
        while True:
            try:
                data = await reader.read(32768)
                if not data:
                    break
                await ws.send_bytes(data)
            except ConnectionClosedOK:
                break
            except Exception as e:
                logger.error(e)
                break


    async def read_from_websocket():
        while True:
            try:
                data = await ws.receive()
                writer.write(data["bytes"])
                await writer.drain()
            except ConnectionClosedOK:
                break
            except Exception as e:
                logger.error(e)
                break

    await asyncio.gather(read_from_vnc(), read_from_websocket())
