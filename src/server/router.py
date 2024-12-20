import asyncio
from fastapi import APIRouter, Request, WebSocket, Form, Depends
from fastapi.responses import RedirectResponse
from src.auth.models import User
from src.auth.utils import active_user, active_user_ws
from src.node.crud import crud_read_node
from src.server.crud import crud_read_servers, crud_read_server
from src.server.vds import vds_install, vds_action, vds_status
from src.payment.crud import crud_read_vds
from src.display.utils import t_error

router = APIRouter(prefix="/api/server", tags=["servers"])


@router.post("/install/{server_id}")
async def install(request: Request, server_id: int, os: str = Form(...), user: User = Depends(active_user)):
    # Check server
    server = await crud_read_server(server_id)

    if not server or not server.is_active or server.user_id != user.id:
        return await t_error(request, 403, "Invalid server")

    if os not in ("debian", "arch", "alpine", "gentoo", "freebsd", "openbsd"):
        return await t_error(request, 422, "Invalid OS")

    # Installation logic
    node = await crud_read_node(server.node_id)
    vds = await crud_read_vds(server.vds_id)

    await vds_install(server, node, vds, os)

    return RedirectResponse("/dashboard", status_code=301)


@router.post("/action/{server_id}")
async def action(request: Request, server_id: int, user: User = Depends(active_user)):
    # Check server
    server = await crud_read_server(server_id)

    if not server or not server.is_active or server.user_id != user.id:
        return await t_error(request, 403, "Invalid server")

    # Action logic
    node = await crud_read_node(server.node_id)

    await vds_action(server, node)

    return RedirectResponse("/dashboard", status_code=301)


@router.websocket("/statuses")
async def statuses(ws: WebSocket, user: User = Depends(active_user_ws)):
    servers = await crud_read_servers(user.id)

    if servers:
        await ws.accept()

        while True:
            stats = []
            time = 5

            for server in servers:
                if server and server.is_active:
                    node = await crud_read_node(server.node_id)
                    status = await vds_status(server, node)

                    if not status["ipv4"]:
                        status["ipv4"] = '-'

                    if not status["ipv6"]:
                        status["ipv6"] = '-'

                    stats.append(status)

                    if len(servers) > time:
                        time = time + 1
            try:
                await ws.send_json(stats)
                await asyncio.sleep(time)
            except Exception:
                pass


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
                data = await reader.read(4096)

                if not data:
                    break

                await ws.send_bytes(data)
            except Exception:
                break

    async def read_from_websocket():
        while True:
            try:
                data = await ws.receive()

                if not data:
                    break

                writer.write(data["bytes"])
                await writer.drain()
            except Exception:
                break

    await asyncio.gather(read_from_vnc(), read_from_websocket())
