import ipaddress
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response, JSONResponse, StreamingResponse
from src.database import r
from src.crud import crud_read
from src.logger import logger
from src.config import SUBNET_IPV4, SUBNET_IPV6, PRODUCTS
from src.payment.schemas import Buy, Pay, Upgrade, QRCode
from src.payment.payments import payment_request
from src.payment.utils import check_active_payment, check_payment_limit, draw_qrcode, xmr_course
from src.server.models import Server
from src.server.schemas import ServerCreate, IPUpdate
from src.server.crud import crud_create_server, crud_read_servers, crud_read_server
from src.node.schemas import NodeUpdate
from src.node.crud import crud_read_nodes, crud_read_node, crud_update_node
from src.user.models import User
from src.auth.utils import active_user

router = APIRouter(prefix="/api/payment", tags=["payments"])


@router.post("/buy")
async def checkout(data: Buy, user: User = Depends(active_user)):
    # Check if user have active payment
    res = await check_active_payment(user.id)

    if res is not None: return res

    # Check user's payment limit
    await check_payment_limit(user.id)

    if not [vps_id for vps_id in PRODUCTS["vps"] if int(vps_id) == data.vps_id]:
        raise HTTPException(status_code=400, detail="This product doesn't exist")

    # Check availability of resources
    if PRODUCTS["vps"][str(data.vps_id)]["ipv4"]:
        subnet = ipaddress.IPv4Network(SUBNET_IPV4)

        for ipv4 in subnet:
            server = await crud_read(Server, Server.ipv4, str(ipv4))
            if server is None: break

        if ipv4 is None:
            raise HTTPException(status_code=400, detail="We haven't available IPv4")

    if PRODUCTS["vps"][str(data.vps_id)]["ipv6"]:
        subnet = ipaddress.IPv6Network(SUBNET_IPV6)

        for ipv6 in subnet:
            server = await crud_read(Server, Server.ipv6, str(ipv6))
            if server is None: break

        if ipv6 is None:
            raise HTTPException(status_code=400, detail="We haven't available IPv6")

    cores = PRODUCTS["vps"][str(data.vps_id)]["cores"]
    ram = PRODUCTS["vps"][str(data.vps_id)]["ram"]
    disk_size = PRODUCTS["vps"][str(data.vps_id)]["disk_size"]

    nodes = await crud_read_nodes(cores, ram, disk_size)

    if not nodes:
        raise HTTPException(status_code=400, detail="We haven't available resources")

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
        vnc_port=vnc_port,
        ipv4=str(ipv4),
        ipv6=None,
        start_at=datetime.utcnow(),
        end_at=datetime.now() + timedelta(days=31),
        is_active=False,
		vps_id=data.vps_id,
        node_id=node.id,
        user_id=user.id
    )
    node_schema = NodeUpdate(
        cores_available=(node.cores_available - cores),
        ram_available=(node.ram_available - ram),
        disk_size_available=(node.disk_size_available - disk_size)
    )

    await crud_update_node(node_schema, node.id)
    server_id = await crud_create_server(server_schema)

    # Make payment request and return it uri
    await r.set(f"inactive_server:{server_id}", server_id, ex=900)

    return await payment_request("buy", server_id)


@router.post("/pay")
async def checkout(data: Pay, user: User = Depends(active_user)):
    # Check if user have active payment
    res = await check_active_payment(user.id)

    if res is not None: return res

    # Check user's payment limit
    await check_payment_limit(user.id)

    # Check expiring date
    server = await crud_read_server(data.server_id)

    if server.end_at - server.start_at > timedelta(days=10):
        raise HTTPException(
            status_code=400, detail="You can't pay for more than 40 days"
        )

    # Make payment request and return it uri
    return await payment_request("pay", data.server_id)


@router.post("/close")
async def close(user: User = Depends(active_user)):
    payment_uri = await r.get(f"payment_uri:{user.id}")

    if payment_uri is not None:
        await r.delete(f"payment_uri:{user.id}")
        return JSONResponse({"detail": "Payment has been closed"}, status_code=204)

    raise HTTPException(status_code=400, detail="You haven't active payments")


@router.post("/qrcode")
async def qrcode(data: QRCode, user: User = Depends(active_user)):
    qrcode = await draw_qrcode(data.uri)

    return StreamingResponse(qrcode, media_type="image/png")


@router.get("/products")
async def products():
    return PRODUCTS


@router.get("/course")
async def course():
    return await xmr_course()
