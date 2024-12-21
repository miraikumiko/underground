import asyncio
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket
from starlette.routing import Route
from src.database import Database
from src.auth.utils import active_user, active_user_ws
from src.server.vds import vds_install, vds_action, vds_status
from src.display.utils import t_error


async def install(request: Request, server_id: int):
    user = await active_user(request)
    form = await request.form()
    os = form.get("os")

    # Check server
    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or not server[4] or server[8] != user[0]:
        return await t_error(request, 403, "Invalid server")

    if os not in ("debian", "arch", "alpine", "gentoo", "freebsd", "openbsd"):
        return await t_error(request, 422, "Invalid OS")

    # Installation logic
    async with Database() as db:
        node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))
        vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (server[6],))

    await vds_install(server, node[1], vds, os)

    return RedirectResponse("/dashboard", status_code=301)


async def action(request: Request, server_id: int):
    user = await active_user(request)

    # Check server
    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or not server[4] or server[8] != user[0]:
        return await t_error(request, 403, "Invalid server")

    # Action logic
    async with Database() as db:
        node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))

    await vds_action(server[0], node[1])

    return RedirectResponse("/dashboard", status_code=301)


async def statuses(ws: WebSocket):
    user = await active_user_ws(ws)

    async with Database() as db:
        servers = await db.fetchall("SELECT * FROM server WHERE user_id = ?", (user[0],))

    if servers:
        await ws.accept()

        try:
            while True:
                stats = []
                time = 5

                for server in servers:
                    if server[4]:
                        async with Database() as db:
                            node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))
                            status = await vds_status(server[0], node[1])

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


async def vnc(server_id: int, ws: WebSocket):
    user = await active_user_ws(ws)

    # Check server
    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or not server[4] or server[8] != user[0]:
        return

    # VNC logic
    await ws.accept()

    async with Database() as db:
        node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))

    try:
        reader, writer = await asyncio.open_connection(node[1], server[1])
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
    Route("/install/{server_id}", install, methods=["POST"]),
    Route("/action/{server_id}", action, methods=["POST"]),
    Route("/statuses", statuses),
    Route("/vnc/{server_id}", vnc)
]
