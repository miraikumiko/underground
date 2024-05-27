from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from src.database import r
from src.logger import logger
from src.payment.schemas import Buy, Pay, Upgrade
from src.payment.payments import payment_request
from src.payment.utils import get_prices, check_active_payment, check_payment_limit
from src.server.schemas import ServerCreate, IPUpdate
from src.server.crud import (
    crud_create_server,
    crud_read_servers,
    crud_read_server,
    crud_read_ipv4s,
    crud_update_ipv4,
    crud_read_ipv6s,
    crud_update_ipv6
)
from src.node.crud import crud_read_nodes, crud_read_node, crud_update_node
from src.node.schemas import NodeUpdate
from src.user.models import User
from src.auth.utils import active_user

router = APIRouter(prefix="/api/payment", tags=["payments"])


@router.post("/buy")
async def buy(data: Buy, user: User = Depends(active_user)):
    # Check if user have active payment
    await check_active_payment(user.id)

    # Check user's payment limit
    await check_payment_limit(user.id)

    # Validate specs
    if data.cores not in (1, 2, 4, 8):
        raise HTTPException(status_code=400, detail="Invalid cores count")
    elif data.ram not in (1024, 2048, 4096, 8192):
        raise HTTPException(status_code=400, detail="Invalid ram count")
    elif data.disk_size not in (32, 64, 128, 256, 512, 1024):
        raise HTTPException(status_code=400, detail="Invalid disk size")
    elif data.month not in (1, 2, 3, 4, 5, 6, 7, 8, 9):
        raise HTTPException(status_code=400, detail="Invalid month count")

    ipv4s = await crud_read_ipv4s(available=True)

    if not ipv4s:
        raise HTTPException(
            status_code=400,
            detail="Haven't available IPv4 addresses"
        )

    ipv4 = ipv4s[0]

    nodes = await crud_read_nodes(data.cores, data.ram, data.disk_size)

    if not nodes:
        raise Exception("Doesn't have available nodes")

    node = nodes[0]

    # Reservation port for VNC
    servers = await crud_read_servers()
    used_ports = []
    vnc_port = 5900

    if servers:
        for server in servers:
            if server.node_id == node.id:
                used_ports.append(server.vnc_port)

        while vnc_port in used_ports:
            vnc_port += 1

    server_schema = ServerCreate(
        cores=data.cores,
        ram=data.ram,
        disk_type="ssd",
        disk_size=data.disk_size,
        traffic=5,
        vnc_port=vnc_port,
        ipv4=ipv4.ip,
        ipv6=None,
        start_at=datetime.utcnow(),
        end_at=datetime.now() + timedelta(days=30 * data.month),
        active=False,
        user_id=user.id,
        node_id=node.id
    )

    # Update availability of node and IPs
    node_schema = NodeUpdate(
        cores_available=(node.cores_available - data.cores),
        ram_available=(node.ram_available - data.ram),
        disk_size_available=(node.disk_size_available - data.disk_size)
    )
    ipv4_schema = IPUpdate(available=False)

    await crud_update_node(node_schema, node.id)
    await crud_update_ipv4(ipv4_schema, ipv4.ip)

    # Make payment request and return it uri
    server_id = await crud_create_server(server_schema)

    await r.set(f"inactive_server:{server_id}", server_id, ex=900)

    return await payment_request(
        "buy",
        user.id,
        server_id,
        data.cores,
        data.ram,
        data.disk_size,
        data.month
    )


@router.post("/pay")
async def pay(data: Pay, user: User = Depends(active_user)):
    # Check if user have active payment
    await check_active_payment(user.id)

    # Check user's payment limit
    await check_payment_limit(user.id)

    # Validate params
    if data.month not in range(1, 10):
        raise HTTPException(status_code=400, detail="Invalid month count")

    server = await crud_read_server(data.server_id)

    if server is None:
        raise HTTPException(status_code=400, detail="Server doesn't exist")

    if ((server.end_at - datetime.now()).days / 30) + data.month > 8:
        raise HTTPException(status_code=400, detail="You can't pay for more than 9 months")

    # Make payment request and return it uri
    return await payment_request(
        "pay",
        user.id,
        data.server_id,
        server.cores,
        server.ram,
        server.disk_size,
        data.month
    )


@router.post("/upgrade")
async def upgrade(data: Upgrade, user: User = Depends(active_user)):
    # Check if user have active payment
    await check_active_payment(user.id)

    # Check user's payment limit
    await check_payment_limit(user.id)

    # Validate specs
    server = await crud_read_server(data.server_id)

    if server is None:
        raise HTTPException(status_code=400, detail="Server doesn't exist")

    prices = await get_prices()

    if data.cores not in prices["cpu"].keys() or data.cores < server.cores:
        raise HTTPException(status_code=400, detail="Invalid cores count")
    elif data.ram not in prices["ram"].keys() or data.ram < server.ram:
        raise HTTPException(status_code=400, detail="Invalid ram count")
    elif data.disk_size not in prices["disk"].keys() or data.disk_size < server.disk_size:
        raise HTTPException(status_code=400, detail="Invalid disk size")
    elif data.month not in range(1, 10):
        raise HTTPException(status_code=400, detail="Invalid month count")

    # Check node specs availability
    node = await crud_read_node(server.node_id)

    if data.cores > node.cores_available:
        raise HTTPException(
            status_code=503, detail="This node haven't available cores"
        )
    elif data.ram > node.ram_available:
        raise HTTPException(
            status_code=503, detail="This node haven't available ram"
        )
    elif data.disk > node.disk_size_available:
        raise HTTPException(
            status_code=503, detail="This node haven't available disk space"
        )

    # Update node available specs
    node_schema = NodeUpdate(
        cores_available=(node.cores_available - data.cores),
        ram_available=(node.ram_available - data.ram),
        disk_size_available=(node.disk_size_available - data.disk_size)
    )

    await crud_update_node(node_schema, node.id)

    # Make payment request and return it uri
    return await payment_request(
        "upgrade",
        user.id,
        data.server_id,
        data.cores,
        data.ram,
        data.disk_size,
        data=f"{server.cores},{server.ram},{server.disk_size}"
    )


@router.post("/close")
async def close(user: User = Depends(active_user)):
    payment_uri = await r.get(f"payment_uri:{user.id}")

    if payment_uri is not None:
        await r.delete(f"payment_uri:{user.id}")
        return Response(status_code=204)
    else:
        return "You haven't active payments"


@router.get("/prices")
async def prices():
    return await get_prices()
