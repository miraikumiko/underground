from datetime import datetime, timedelta
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException
from src.config import VDS_DAYS, VDS_MAX_PAYED_DAYS
from src.database import execute, fetchone, fetchall
from src.auth.utils import active_user
from src.payment.utils import request_vds
from src.server.utils import vds_migrate, vds_upgrade
from src.display.utils import no_cache_headers


async def buy(request: Request):
    user = await active_user(request)
    product_id = request.path_params.get("product_id")
    vds = await fetchone("SELECT * FROM vds WHERE id = ?", (product_id,))

    if not vds:
        raise HTTPException(400, "This product doesn't exist")

    # Check availability of resources
    nodes = await fetchall(
        "SELECT * FROM node WHERE cores_available >= ? AND ram_available >= ? AND disk_size_available >= ?",
        (vds["cores"], vds["ram"], vds["disk_size"])
    )

    if not nodes:
        raise HTTPException(503, "We haven't available resources")

    # Buy VDS
    if user["balance"] < vds["price"]:
        return RedirectResponse(f"/checkout/{product_id}", 301, no_cache_headers)

    await execute(
        "UPDATE user SET balance = ? WHERE id = ?",
        (user["balance"] - vds["price"], user["id"])
    )

    await request_vds(user["id"], vds, nodes[0])

    return RedirectResponse("/dashboard", 301, no_cache_headers)


async def pay(request: Request):
    user = await active_user(request)
    server_id = request.path_params.get("server_id")
    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    # Check server
    if not server or server["user_id"] != user["id"]:
        raise HTTPException(400, "Invalid server")

    # Check rent limit
    server_end_at = datetime.strptime(server["end_at"], "%Y-%m-%d %H:%M:%S.%f")
    server_start_at = datetime.strptime(server["start_at"], "%Y-%m-%d %H:%M:%S.%f")

    if server_end_at - server_start_at + timedelta(days=VDS_DAYS) > timedelta(days=VDS_MAX_PAYED_DAYS):
        raise HTTPException(400, f"You can't pay for more than {VDS_MAX_PAYED_DAYS} days")

    # Pay VDS
    vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))

    if user["balance"] < vds["price"]:
        raise HTTPException(400, "You haven't enough money")

    await execute(
        "UPDATE user SET balance = ? WHERE id = ?",
        (user["balance"] - vds["price"], user["id"])
    )

    end_at = datetime.strptime(server["end_at"], "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=VDS_DAYS)

    await execute("UPDATE server SET end_at = ? WHERE id = ?", (end_at, server["id"]))

    return RedirectResponse("/dashboard", 301, no_cache_headers)


async def upgrade(request: Request):
    user = await active_user(request)
    server_id = request.path_params.get("server_id")
    product_id = request.path_params.get("product_id")

    # Validate product id
    upgrade_vds = await fetchone("SELECT * FROM vds WHERE id = ?", (product_id,))

    if not upgrade_vds:
        raise HTTPException(400, "This product doesn't exist")

    # Check server
    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or server["user_id"] != user["id"] or server["vds_id"] >= upgrade_vds["id"]:
        raise HTTPException(400, "Invalid server")

    # Check availability of resources
    node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
    server_vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))
    nodes = await fetchall(
        "SELECT * FROM node WHERE cores_available >= ? AND ram_available >= ? AND disk_size_available >= ?",
        (upgrade_vds["cores"], upgrade_vds["ram"], upgrade_vds["disk_size"])
    )

    if not nodes:
        raise HTTPException(503, "We haven't available resources")

    # Upgrade VDS
    if user["balance"] < upgrade_vds["price"]:
        raise HTTPException(400, "You haven't enough money")

    await execute(
        "UPDATE user SET balance = ? WHERE id = ?",
        (user["balance"] - upgrade_vds["price"] + server_vds["price"], user["id"])
    )

    if node in nodes:
        await execute(
            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
            (
                node["cores_available"] - upgrade_vds["cores"] + server_vds["cores"],
                node["ram_available"] - upgrade_vds["ram"] + server_vds["ram"],
                node["disk_size_available"] - upgrade_vds["disk_size"] + server_vds["disk_size"],
                server["node_id"]
            )
        )
        await execute(
            "UPDATE server SET vds_id = ? WHERE id = ?",
            (upgrade_vds["id"], server["id"])
        )

        await vds_upgrade(server["id"], node["ip"], server_vds)
    else:
        dst_node = nodes[0]

        await execute(
            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
            (
                node["cores_available"] + server_vds["cores"],
                node["ram_available"] + server_vds["ram"],
                node["disk_size_available"] + server_vds["disk_size"],
                node["id"]
            )
        )
        await execute(
            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
            (
                dst_node["cores_available"] - upgrade_vds["cores"],
                dst_node["ram_available"] - upgrade_vds["ram"],
                dst_node["disk_size_available"] - upgrade_vds["disk_size"],
                dst_node["id"]
            )
        )
        await execute(
            "UPDATE server SET vds_id = ?, node_id = ? WHERE id = ?",
            (upgrade_vds["id"], dst_node["id"], server["id"])
        )

        await vds_upgrade(server["id"], node["ip"], server_vds)
        await vds_migrate(server["id"], node["ip"], dst_node)

    return RedirectResponse("/dashboard", 301, no_cache_headers)


async def promo(request: Request):
    user = await active_user(request)
    form = await request.form()
    code = form.get("code")

    if not code:
        raise HTTPException(400, "The code field is required")

    promo_code = await fetchone("SELECT * FROM promo WHERE code = ?", (code,))

    if not promo_code:
        raise HTTPException(400, "Invalid promo code")

    vds = await fetchone("SELECT * FROM vds WHERE id = ?", (promo_code["vds_id"],))
    nodes = await fetchall(
        "SELECT * FROM node WHERE cores_available >= ? AND ram_available >= ? AND disk_size_available >= ?",
        (vds["cores"], vds["ram"], vds["disk_size"])
    )

    if not nodes:
        raise HTTPException(503, "We haven't available resources")

    await request_vds(user["id"], vds, nodes[0])

    await execute("DELETE FROM promo WHERE id = ?", (promo_code["id"],))

    return RedirectResponse("/dashboard", 301, no_cache_headers)


payment_router = [
    Route("/buy/{product_id:int}", buy, methods=["GET"]),
    Route("/pay/{server_id:int}", pay, methods=["GET"]),
    Route("/upgrade/{server_id:int}/{product_id:int}", upgrade, methods=["GET"]),
    Route("/promo", promo, methods=["POST"])
]
