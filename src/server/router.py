import asyncio
from fastapi import APIRouter, Request, WebSocket, Form, Depends
from fastapi.responses import RedirectResponse
from src.user.models import User
from src.auth.utils import active_user, active_user_ws
from src.node.crud import crud_read_node
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_servers, crud_read_server, crud_update_server
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
    # Check server
    servers = await crud_read_servers(user.id)

    # Statuses logic
    if servers:
        await ws.accept()

        while True:
            try:
                stats = []
                time = 5

                for server in servers:
                    if server and server.is_active:
                        node = await crud_read_node(server.node_id)
                        stat = await vds_status(server, node)

                        if stat["ipv4"] or stat["ipv6"]:
                            if not server.ipv4 or server.ipv4 != stat["ipv4"]:
                                server_schema = ServerUpdate(ipv4=stat["ipv4"])
                                server_schema = server_schema.rm_none_attrs()
                                await crud_update_server(server_schema, server.id)

                            if not server.ipv6 or server.ipv6 != stat["ipv6"]:
                                server_schema = ServerUpdate(ipv6=stat["ipv6"])
                                server_schema = server_schema.rm_none_attrs()
                                await crud_update_server(server_schema, server.id)
                        else:
                            if not server.ipv4:
                                stat["ipv4"] = '-'
                            else:
                                stat["ipv4"] = server.ipv4

                            if not server.ipv6:
                                stat["ipv6"] = '-'
                            else:
                                stat["ipv6"] = server.ipv6

                        if not stat["status"]:
                            stat["status"] = '-'

                        stats.append(stat)

                        if len(servers) > time:
                            time = time + 1

                await ws.send_json(stats)
                await asyncio.sleep(time)
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
