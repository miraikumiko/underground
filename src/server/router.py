import asyncio
from fastapi import APIRouter, Request, WebSocket, Form, Depends
from fastapi.responses import RedirectResponse
from src.server.crud import crud_read_server
from src.server.vds import vds_install, vds_action, vds_status
from src.node.crud import crud_read_node
from src.user.models import User
from src.auth.utils import active_user, active_user_ws
from src.display.utils import t_error

router = APIRouter(prefix="/api/server", tags=["servers"])


@router.post("/install/{server_id}")
async def install(request: Request, server_id: int, os: str = Form(...), user: User = Depends(active_user)):
    # Check server
    server = await crud_read_server(server_id)

    if server is None or not server.is_active or server.user_id != user.id:
        return await t_error(request, 403, "Invalid server")

    # Action logic
    try:
        await vds_install(server, os)
        return RedirectResponse("/dashboard", status_code=301)
    except ValueError as e:
        return await t_error(request, 422, str(e))


@router.post("/action/{server_id}")
async def action(request: Request, server_id: int, user: User = Depends(active_user)):
    # Check server
    server = await crud_read_server(server_id)

    if server is None or not server.is_active or server.user_id != user.id:
        return await t_error(request, 403, "Invalid server")

    # Action logic
    await vds_action(server_id)

    return RedirectResponse("/dashboard", status_code=301)


@router.websocket("/status/{server_id}")
async def status(server_id: int, ws: WebSocket, user: User = Depends(active_user_ws)):
    # Check server
    server = await crud_read_server(server_id)

    if not server or not server.is_active or server.user_id != user.id:
        return None

    # Status logic
    await ws.accept()

    while True:
        try:
            stat = await vds_status(server_id)
            await ws.send_json(stat)
            await asyncio.sleep(5)
        except Exception:
            break


@router.websocket("/vnc/{server_id}")
async def vnc(server_id: int, ws: WebSocket, user: User = Depends(active_user_ws)):
    # Check server
    server = await crud_read_server(server_id)

    if server is None or not server.is_active or server.user_id != user.id:
        return None

    # VNC logic
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
            except Exception:
                break

    async def read_from_websocket():
        while True:
            try:
                data = await ws.receive()
                writer.write(data["bytes"])
                await writer.drain()
            except Exception:
                break

    await asyncio.gather(read_from_vnc(), read_from_websocket())
