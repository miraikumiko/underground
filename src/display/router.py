import base64
import ipaddress
from uuid import uuid4
from random import choice, randint
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from captcha.image import ImageCaptcha
from src.database import r
from src.crud import crud_read
from src.config import SUBNET_IPV4, SUBNET_IPV6, PRODUCTS
from src.user.models import User
from src.auth.utils import active_user
from src.server.models import Server
from src.server.schemas import ServerCreate
from src.server.crud import crud_create_server, crud_read_servers, crud_read_server
from src.server.vps import vps_status
from src.node.schemas import NodeUpdate
from src.node.crud import crud_read_nodes, crud_read_node, crud_update_node
from src.payment.payments import payment_request
from src.payment.utils import check_active_payment, check_payment_limit, draw_qrcode, xmr_course
from src.display.utils import templates

router = APIRouter()


@router.get("/")
async def index(request: Request, user: User = Depends(active_user)):
    course = await xmr_course()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "course": course,
        "products": PRODUCTS["vps"]
    })


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register(request: Request):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    text = ''.join(choice(chars) for _ in range(randint(5, 7)))
    captcha_id = randint(10000000, 99999999)

    image = ImageCaptcha(width=218, height=50)
    captcha = base64.b64encode(image.generate(text).getvalue()).decode("utf-8")

    await r.set(f"captcha:{captcha_id}", text, ex=90)

    return templates.TemplateResponse("register.html", {
        "request": request, "captcha_id": captcha_id, "captcha": captcha
    })


@router.get("/reset-password")
async def change_password(request: Request, _: User = Depends(active_user)):
    return templates.TemplateResponse("change-password.html", {"request": request})


@router.get("/delete-account")
async def delete_account(request: Request, _: User = Depends(active_user)):
    return templates.TemplateResponse("delete-account.html", {"request": request})


@router.post("/logout")
async def logout(_: User = Depends(active_user)):
    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure'
    })


@router.get("/dashboard")
async def dashboard(request: Request, user: User = Depends(active_user)):
    course = await xmr_course()
    servers = await crud_read_servers(user.id)
    servers = [server for server in servers if server.is_active]

    return templates.TemplateResponse("dashboard.html", {
      "request": request,
      "user": user,
      "course": course,
      "servers": servers
    })


@router.get("/buy/{product_id}")
async def buy(product_id: int, request: Request, user: User = Depends(active_user)):
    # Check auth
    if user is None:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Unauthorized",
            "msg2": "Please login"
        })

    # Check if user have active payment
    await check_active_payment(user.id)

    # Check user's payment limit
    await check_payment_limit(user.id)

    # Validate product id
    if not [vps_id for vps_id in PRODUCTS["vps"] if int(vps_id) == product_id]:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "This product doesn't exist"
        })

    # Define vars
    servers = await crud_read_servers()
    ipv4 = None
    ipv6 = None

    # Check availability of IPv4
    if PRODUCTS["vps"][str(product_id)]["ipv4"]:
        subnet = ipaddress.IPv4Network(SUBNET_IPV4)

        if servers:
            reserved_ipv4s = [server.ipv4 for server in servers]
            ipv4s = [ipv4 for ipv4 in subnet if ipv4 not in reserved_ipv4s].reverse()

            if not ipv4s:
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "msg1": "Service Unavailable",
                    "msg2": "We haven't available IPv4"
                })

            ipv4 = ipv4s[0]
        else:
            ipv4 = subnet[-1]

    # Check availability of IPv6
    if PRODUCTS["vps"][str(product_id)]["ipv6"]:
        subnet = ipaddress.IPv4Network(SUBNET_IPV4)

        if servers:
            reserved_ipv6s = [server.ipv6 for server in servers]
            ipv6s = [ipv6 for ipv6 in subnet if ipv6 not in reserved_ipv6s].reverse()

            if not ipv6s:
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "msg1": "Service Unavailable",
                    "msg2": "We haven't available IPv6"
                })

            ipv6 = ipv6s[0]
        else:
            ipv6 = subnet[-1]

    # Check availability of resources
    cores = PRODUCTS["vps"][str(product_id)]["cores"]
    ram = PRODUCTS["vps"][str(product_id)]["ram"]
    disk_size = PRODUCTS["vps"][str(product_id)]["disk_size"]

    nodes = await crud_read_nodes(cores, ram, disk_size)

    if not nodes:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Service Unavailable",
            "msg2": "We haven't available resources"
        })

    node = nodes[0]

    # Reservation port for VNC
    vnc_port = 5900

    if servers:
        up = [server.vnc_port for server in servers if server.node_id == node.id]
        while vnc_port in up: vnc_port += 1

    # Registration of new server
    server_schema = ServerCreate(
        vnc_port=vnc_port,
        ipv4=str(ipv4),
        ipv6=str(ipv6),
        start_at=datetime.utcnow(),
        end_at=datetime.now() + timedelta(days=31),
        is_active=False,
        vps_id=product_id,
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

    payment_data = await payment_request("buy", server_id)
    qrcode = await draw_qrcode(payment_data["payment_uri"])

    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "qrcode": qrcode,
        "uri": payment_data["payment_uri"],
        "ttl": payment_data["ttl"]
    })


@router.get("/pay/{server_id}")
async def pay(server_id: int, request: Request, user: User = Depends(active_user)):
    # Check auth
    if user is None:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Unauthorized",
            "msg2": "Please login"
        })

    # Check server
    server = await crud_read_server(server_id)

    if server is None or server.user_id != user.id:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "Invalid server"
        })
 
    # Check if user have active payment
    await check_active_payment(user.id)

    # Check user's payment limit
    await check_payment_limit(user.id)

    # Check expiring date
    server = await crud_read_server(server_id)

    if server.end_at - server.start_at > timedelta(days=10):
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "You can't pay for more than 40 days"
        })

    # Make payment request and return it uri
    payment_data = await payment_request("pay", server_id)
    qrcode = await draw_qrcode(payment_data["payment_uri"])

    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "qrcode": qrcode,
        "uri": payment_data["payment_uri"],
        "ttl": payment_data["ttl"]
    })


@router.get("/upgrademenu/{server_id}")
async def upgrade(server_id: int, request: Request, user: User = Depends(active_user)):
    server = await crud_read_server(server_id)
    products = {key: value for key, value in PRODUCTS["vps"].items() if int(key) > server.vps_id}

    return templates.TemplateResponse("upgrade.html", {
      "request": request,
      "products": products,
      "server_id": server_id
    })


@router.get("/install/{server_id}")
async def install(server_id: int, request: Request, user: User = Depends(active_user)):
    return templates.TemplateResponse("install.html", {
      "request": request,
      "server_id": server_id
    })


@router.get("/vnc/{server_id}")
async def vnc(server_id: int, request: Request, user: User = Depends(active_user)):
    return templates.TemplateResponse("vnc.html", {"request": request})
