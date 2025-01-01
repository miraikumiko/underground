import asyncio
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.routing import Route, WebSocketRoute
from src.database import fetchone
from src.auth.utils import active_user, active_user_ws
from src.server.utils import vds_install, vds_action
from src.display.utils import t_error


async def install(request: Request):
    user = await active_user(request)
    form = await request.form()
    os_name = form.get("os")
    server_id = request.path_params.get("server_id")

    if not os_name or not server_id:
        return await t_error(request, 400, "The fields os and server_id are required")

    # Check server
    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or server["user_id"] != user["id"]:
        return await t_error(request, 403, "Invalid server")

    # Check os
    os = await fetchone("SELECT * FROM os WHERE name = ?", (os_name,))

    if not os:
        return await t_error(request, 422, "Invalid OS")

    # Installation logic
    node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
    vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))

    await vds_install(server, node["ip"], vds, os_name)

    return RedirectResponse("/dashboard", 301)


async def action(request: Request):
    user = await active_user(request)
    server_id = request.path_params.get("server_id")

    if not server_id:
        return await t_error(request, 400, "The field server_id is required")

    # Check server
    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or server["user_id"] != user["id"]:
        return await t_error(request, 403, "Invalid server")

    # Action logic
    node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))

    await vds_action(server["id"], node["ip"])

    return RedirectResponse("/dashboard", 301)


async def vnc(ws: WebSocket):
    user = await active_user_ws(ws)
    server_id = ws.path_params.get("server_id")

    if not server_id:
        raise WebSocketDisconnect(code=1008)

    # Check server
    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or server["user_id"] != user["id"]:
        raise WebSocketDisconnect(code=1008)

    # VNC logic
    await ws.accept()

    node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))

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
            except RuntimeError:
                break

    async def read_from_websocket():
        while True:
            data = await ws.receive()
            b = data.get("bytes")

            if not b:
                break

            writer.write(b)
            await writer.drain()

    await asyncio.gather(read_from_vnc(), read_from_websocket())


server_router = [
    Route("/install/{server_id:int}", install, methods=["POST"]),
    Route("/action/{server_id:int}", action, methods=["POST"]),
    WebSocketRoute("/vnc/{server_id:int}", vnc)
]
