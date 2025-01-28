from datetime import datetime, timedelta
from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException
from underground.config import VDS_DAYS, VDS_MAX_PAYED_DAYS
from underground.database import database
from underground.models import User, Promocode, VDS, Node, Server
from underground.utils.payment import request_vds
from underground.utils.server import vds_migrate, vds_upgrade
from underground.utils.display import no_cache_headers


@requires("authenticated")
async def buy(request: Request):
    user = request.user
    product_id = request.path_params.get("product_id")
    vds = await database.fetch_one(VDS.select().where(VDS.c.id == product_id))

    if not vds:
        raise HTTPException(400, "This product doesn't exist")

    # Check availability of resources
    nodes = await database.fetch_all(
        Node.select().where(Node.c.cores_available >= vds.cores and Node.c.ram_available >= vds.ram and Node.c.disk_size_available >= vds.disk_size)
    )

    if not nodes:
        raise HTTPException(503, "We haven't available resources")

    # Buy VDS
    if user.balance < vds.price:
        return RedirectResponse(f"/checkout/{product_id}", 301, no_cache_headers)

    await database.execute(User.update().where(User.c.id == user.id).values(balance=user.balance - vds.price))

    await request_vds(user.id, vds, nodes[0])

    return RedirectResponse("/dashboard", 301, no_cache_headers)


@requires("authenticated")
async def pay(request: Request):
    user = request.user
    server_id = request.path_params.get("server_id")
    server = await database.fetch_one(Server.select().where(Server.c.id == server_id))

    # Check server
    if not server or server.user_id != user.id:
        raise HTTPException(400, "Invalid server")

    # Check rent limit
    server_end_at = datetime.fromisoformat(server.end_at)
    server_start_at = datetime.fromisoformat(server.start_at)

    if server_end_at - server_start_at + timedelta(days=VDS_DAYS) > timedelta(days=VDS_MAX_PAYED_DAYS):
        raise HTTPException(400, f"You can't pay for more than {VDS_MAX_PAYED_DAYS} days")

    # Pay VDS
    vds = await database.fetch_one(VDS.select().where(VDS.c.id == server.vds_id))

    if user.balance < vds.price:
        raise HTTPException(400, "You haven't enough money")

    await database.execute(User.update().where(User.c.id == user.id).values(balance=user.balance - vds.price))

    end_at = (datetime.fromisoformat(server.end_at) + timedelta(days=VDS_DAYS)).strftime("%Y-%m-%d %H:%M:%S")

    await database.execute(Server.update().where(Server.c.id == server.id).values(end_at=end_at))

    return RedirectResponse("/dashboard", 301, no_cache_headers)


@requires("authenticated")
async def upgrade(request: Request):
    user = request.user
    server_id = request.path_params.get("server_id")
    product_id = request.path_params.get("product_id")

    # Validate product id
    upgrade_vds = await database.fetch_one(VDS.select().where(VDS.c.id == product_id))

    if not upgrade_vds:
        raise HTTPException(400, "This product doesn't exist")

    # Check server
    server = await database.fetch_one(Server.select().where(Server.c.id == server_id))

    if not server or server.user_id != user.id or server.vds_id >= upgrade_vds.id:
        raise HTTPException(400, "Invalid server")

    # Check availability of resources
    node = await database.fetch_one(Node.select().where(Node.c.id == server.node_id))
    server_vds = await database.fetch_one(VDS.select().where(VDS.c.id == server.vds_id))
    nodes = await database.fetch_all(
        Node.select().where(Node.c.cores_available >= upgrade_vds.cores and Node.c.ram_available >= upgrade_vds.ram and Node.c.disk_size_available >= upgrade_vds.disk_size)
    )

    if not nodes:
        raise HTTPException(503, "We haven't available resources")

    # Upgrade VDS
    if user.balance < upgrade_vds.price:
        raise HTTPException(400, "You haven't enough money")

    await database.execute(User.update().where(User.c.id == user.id).values(balance=user.balance - upgrade_vds.price + server_vds.price))

    if node in nodes:
        await database.execute(
            Node.update().where(Node.c.id == server.node_id).values(
                cores_available=node.cores_available - upgrade_vds.cores + server_vds.cores,
                ram_available=node.ram_available - upgrade_vds.ram + server_vds.ram,
                disk_size_available=node.disk_size_available - upgrade_vds.disk_size + server_vds.disk_size
            )
        )
        await database.execute(Server.update().where(Server.c.id == server.id).values(vds_id=upgrade_vds.id))

        await vds_upgrade(server.id, node.ip, server_vds)
    else:
        dst_node = nodes[0]

        await database.execute(
            Node.update().where(Node.c.id == node.id).values(
                cores_available=node.cores_available + server_vds.cores,
                ram_available=node.ram_available + server_vds.ram,
                disk_size_available=node.disk_size_available + server_vds.disk_size
            )
        )
        await database.execute(
            Node.update().where(Node.c.id == dst_node.id).values(
                cores_available=dst_node.cores_available - upgrade_vds.cores,
                ram_available=dst_node.ram_available - upgrade_vds.ram,
                disk_size_available=dst_node.disk_size_available - upgrade_vds.disk_size
            )
        )
        await database.execute(Server.update().where(Server.c.id == server.id).values(vds_id=upgrade_vds.id, node_id=dst_node.id))

        await vds_upgrade(server.id, node.ip, server_vds)
        await vds_migrate(server.id, node.ip, dst_node)

    return RedirectResponse("/dashboard", 301, no_cache_headers)


@requires("authenticated")
async def promo(request: Request):
    user = request.user
    form = await request.form()
    code = form.get("code")

    if not code:
        raise HTTPException(400, "The code field is required")

    promo_code = await database.fetch_one(Promocode.select().where(Promocode.c.code == code))

    if not promo_code:
        raise HTTPException(400, "Invalid promo code")

    vds = await database.fetch_one(VDS.select().where(VDS.c.id == promo_code.vds_id))
    nodes = await database.fetch_all(
        Node.select().where(Node.c.cores_available >= vds.cores and Node.c.ram_available >= vds.ram and Node.c.disk_size_available >= vds.disk_size)
    )

    if not nodes:
        raise HTTPException(503, "We haven't available resources")

    await request_vds(user.id, vds, nodes[0])

    await database.execute(Promocode.delete().where(Promocode.c.id == promo_code.id))

    return RedirectResponse("/dashboard", 301, no_cache_headers)


payment_router = [
    Route("/buy/{product_id:int}", buy, methods=["GET"]),
    Route("/pay/{server_id:int}", pay, methods=["GET"]),
    Route("/upgrade/{server_id:int}/{product_id:int}", upgrade, methods=["GET"]),
    Route("/promo", promo, methods=["POST"])
]
