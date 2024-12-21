import asyncio
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket
from starlette.routing import Route, WebSocketRoute
from src.database import Database
from src.auth.utils import active_user, active_user_ws
from src.server.vds import vds_install, vds_action, vds_status
from src.display.utils import t_error


async def install(request: Request):
    user = await active_user(request)
    server_id = request.path_params["server_id"]
    form = await request.form()
    os = form.get("os")

    # Check server
    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or not server["is_active"] or server["user_id"] != user["id"]:
        return await t_error(request, 403, "Invalid server")

    if os not in ("debian", "arch", "alpine", "gentoo", "freebsd", "openbsd"):
        return await t_error(request, 422, "Invalid OS")

    # Installation logic
    async with Database() as db:
        node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
        vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))

    await vds_install(server, node["ip"], vds, os)

    return RedirectResponse("/dashboard", status_code=301)


async def action(request: Request):
    user = await active_user(request)
    server_id = request.path_params["server_id"]

    # Check server
    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or not server["is_active"] or server["user_id"] != user["id"]:
        return await t_error(request, 403, "Invalid server")

    # Action logic
    async with Database() as db:
        node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))

    await vds_action(server["id"], node["ip"])

    return RedirectResponse("/dashboard", status_code=301)


async def statuses(ws: WebSocket):
    user = await active_user_ws(ws)

    async with Database() as db:
        servers = await db.fetchall("SELECT * FROM server WHERE user_id = ?", (user["id"],))

    if servers:
        await ws.accept()

        try:
            while True:
                stats = []
                time = 5

                for server in servers:
                    if server["is_active"]:
                        async with Database() as db:
                            node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
                            status = await vds_status(server["id"], node["ip"])

                        if not status["ipv4"]:
                            status["ipv4"] = '-'

                        if not status["ipv6"]:
                            status["ipv6"] = '-'

                        stats.append(status)

                        if len(servers) > time:
                            time = time + 1

                        await ws.send_json(stats)
                        await asyncio.sleep(time)
        except Exception:
            pass


async def vnc(ws: WebSocket):
    user = await active_user_ws(ws)
    server_id = ws.path_params["server_id"]

    # Check server
    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or not server["is_active"] or server["user_id"] != user["id"]:
        return

    # VNC logic
    await ws.accept()

    async with Database() as db:
        node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))

    try:
        reader, writer = await asyncio.open_connection(node["ip"], server["vnc_port"])
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
                writer.write(data["bytes"])
                await writer.drain()
            except Exception:
                break

    await asyncio.gather(read_from_vnc(), read_from_websocket())


router = [
    Route("/install/{server_id:int}", install, methods=["POST"]),
    Route("/action/{server_id:int}", action, methods=["POST"]),
    WebSocketRoute("/statuses", statuses),
    WebSocketRoute("/vnc/{server_id:int}", vnc)
]
