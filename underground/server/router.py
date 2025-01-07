import asyncio
from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.routing import Route, WebSocketRoute
from starlette.exceptions import HTTPException
from underground.database import fetchone
from underground.server.utils import vds_install, vds_action


@requires("authenticated")
async def install(request: Request):
    user = request.user
    form = await request.form()
    os_name = form.get("os")
    server_id = request.path_params.get("server_id")

    if not os_name:
        raise HTTPException(400, "The field os is required")

    # Check server
    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or server["user_id"] != user["id"]:
        raise HTTPException(403, "Invalid server")

    # Check os
    os = await fetchone("SELECT * FROM os WHERE name = ?", (os_name,))

    if not os:
        raise HTTPException(422, "Invalid OS")

    # Installation logic
    node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
    vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))

    await vds_install(server, node["ip"], vds, os_name)

    return RedirectResponse("/dashboard", 301)


@requires("authenticated")
async def action(request: Request):
    user = request.user
    server_id = request.path_params.get("server_id")
    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    # Check server
    if not server or server["user_id"] != user["id"]:
        raise HTTPException(403, "Invalid server")

    # Action logic
    node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))

    await vds_action(server["id"], node["ip"])

    return RedirectResponse("/dashboard", 301)


@requires("authenticated")
async def vnc(websocket: WebSocket):
    user = websocket.user
    server_id = websocket.path_params.get("server_id")
    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    # Check server
    if not server or server["user_id"] != user["id"]:
        raise WebSocketDisconnect(code=1008)

    # VNC logic
    await websocket.accept()

    node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))

    try:
        reader, writer = await asyncio.open_connection(node["ip"], server["vnc_port"])
    except ConnectionRefusedError:
        return await websocket.close(1013, "VNC Server isn't running now")

    async def read_from_vnc():
        while True:
            try:
                data = await reader.read(4096)
                if not data:
                    break
                await websocket.send_bytes(data)
            except RuntimeError:
                break

    async def read_from_websocket():
        while True:
            data = await websocket.receive()
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
