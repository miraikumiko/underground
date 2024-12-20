from datetime import timedelta
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from src.database import r
from src.config import REGISTRATION, VDS_DAYS, VDS_MAX_PAYED_DAYS, PAYMENT_TIME
from src.user.models import User
from src.auth.utils import active_user, active_user_opt
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_servers, crud_read_server, crud_update_server
from src.server.vds import vds_status
from src.server.utils import request_vds
from src.node.schemas import NodeUpdate
from src.node.crud import crud_read_nodes, crud_read_node, crud_update_node
from src.payment.crud import crud_read_vdss, crud_read_vds
from src.payment.payments import payment_request
from src.payment.utils import check_active_payment, check_payment_limit, xmr_course
from src.display.utils import templates, t_error, t_checkout, get_captcha_base64, draw_qrcode

router = APIRouter()


@router.get("/")
async def index(request: Request, user: User = Depends(active_user_opt)):
    if user:
        servers = await crud_read_servers(user.id)
        servers = [server for server in servers if server.is_active]
    else:
        servers = None

    course = await xmr_course()
    vdss = await crud_read_vdss()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "servers": servers,
        "course": course,
        "vdss": vdss
    })


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register(request: Request):
    if not REGISTRATION:
        return await t_error(request, 400, "Registration is disabled")

    captcha_id, captcha_base64 = await get_captcha_base64()

    return templates.TemplateResponse("register.html", {
        "request": request, "captcha_id": captcha_id, "captcha_base64": captcha_base64
    })


@router.get("/reset-password")
async def change_password(request: Request, _: User = Depends(active_user)):
    return templates.TemplateResponse("change-password.html", {"request": request})


@router.get("/delete-account")
async def delete_account(request: Request, _: User = Depends(active_user)):
    return templates.TemplateResponse("delete-account.html", {"request": request})


@router.get("/dashboard")
async def dashboard(request: Request, user: User = Depends(active_user)):
    course = await xmr_course()
    servers = await crud_read_servers(user.id)
    servers = [server for server in servers if server.is_active]
    statuses = []

    if not servers:
        return RedirectResponse('/', status_code=301)

    for server in servers:
        node = await crud_read_node(server.node_id)
        status = await vds_status(server, node)

        if not status["ipv4"]:
            status["ipv4"] = '-'

        if not status["ipv6"]:
            status["ipv6"] = '-'

        statuses.append(status)

    servers_and_statuses = zip(servers, statuses)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "course": course,
        "servers_and_statuses": servers_and_statuses
    })


@router.get("/promo")
async def promo(request: Request, _: User = Depends(active_user)):
    return templates.TemplateResponse("promo.html", {"request": request})


@router.get("/faq")
async def faq(request: Request, user: User = Depends(active_user_opt)):
    active_servers = []
    course = await xmr_course()

    if user:
        servers = await crud_read_servers(user.id)
        active_servers = [server for server in servers if server.is_active]

    return templates.TemplateResponse("faq.html", {
        "request": request,
        "user": user,
        "servers": active_servers,
        "course": course
    })


@router.get("/install/{server_id}")
async def install(server_id: int, request: Request, _: User = Depends(active_user)):
    return templates.TemplateResponse("install.html", {
        "request": request,
        "server_id": server_id
    })


@router.get("/vnc/{server_id}")
async def vnc(server_id: int, request: Request, _: User = Depends(active_user)):
    return templates.TemplateResponse("vnc.html", {
        "request": request,
        "server_id": server_id
    })


@router.get("/buy/{product_id}")
async def buy(product_id: int, request: Request, user: User = Depends(active_user)):
    # Check if user have active payment
    cap = await check_active_payment(user.id)

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user.id)

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    server_id = await request_vds(product_id, user)

    # Make payment request and return it uri
    await r.set(f"inactive_server:{server_id}", server_id, ex=60 * PAYMENT_TIME)

    payment_data = await payment_request("buy", server_id)
    qrcode = await draw_qrcode(payment_data["payment_uri"])

    return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])


@router.get("/pay/{server_id}")
async def pay(server_id: int, request: Request, user: User = Depends(active_user)):
    # Check server
    server = await crud_read_server(server_id)

    if not server or server.user_id != user.id:
        return await t_error(request, 400, "Invalid server")
 
    # Check if user have active payment
    cap = await check_active_payment(user.id)

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user.id)

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    # Check expiring date
    server = await crud_read_server(server_id)

    if server.end_at - server.start_at > timedelta(days=VDS_MAX_PAYED_DAYS - VDS_DAYS):
        return await t_error(request, 400, f"You can't pay for more than {VDS_MAX_PAYED_DAYS} days")

    # Make payment request and return it uri
    payment_data = await payment_request("pay", server_id)
    qrcode = await draw_qrcode(payment_data["payment_uri"])

    return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])


@router.get("/upgrademenu/{server_id}")
async def upgrademenu(server_id: int, request: Request, _: User = Depends(active_user)):
    server = await crud_read_server(server_id)
    vdss = await crud_read_vdss()
    vdss = [vds for vds in vdss if vds.id > server.vds_id]

    if not vdss:
        return await t_error(request, 400, "Your VDS is already fully upgraded")

    return templates.TemplateResponse("upgrade.html", {
        "request": request,
        "vdss": vdss,
        "server_id": server_id
    })


@router.get("/upgrade/{server_id}")
async def upgrade(server_id: int, product_id: int, request: Request, user: User = Depends(active_user)):
    # Check server
    server = await crud_read_server(server_id)

    if not server or not server.is_active or server.user_id != user.id or server.vds_id >= product_id:
        return await t_error(request, 400, "Invalid server")

    # Check if user have active payment
    cap = await check_active_payment(user.id)

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user.id)

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    # Validate product id
    upgrade_vds = await crud_read_vds(product_id)

    if not upgrade_vds:
        return await t_error(request, 400, "This product doesn't exist")

    # Check availability of resources
    node = await crud_read_node(server.node_id)
    server_vds = await crud_read_vds(server.vds_id)

    nodes = await crud_read_nodes(upgrade_vds.cores, upgrade_vds.ram, upgrade_vds.disk_size)

    if nodes:
        if node in nodes:
            node_schema = NodeUpdate(
                cores_available=node.cores_available - upgrade_vds.cores + server_vds.cores,
                ram_available=node.ram_available - upgrade_vds.ram + server_vds.ram,
                disk_size_available=node.disk_size_available - upgrade_vds.disk_size + server_vds.disk_size
            )
            await crud_update_node(node_schema, server.node_id)
        else:
            dst_node = nodes[0]
            await r.set(f"node_to_migrate:{server_id}", dst_node.id)

            node_schema = NodeUpdate(
                cores_available=dst_node.cores_available - upgrade_vds.cores + server_vds.cores,
                ram_available=dst_node.ram_available - upgrade_vds.ram + server_vds.ram,
                disk_size_available=dst_node.disk_size_available - upgrade_vds.disk_size + server_vds.disk_size
            )
            await crud_update_node(node_schema, dst_node.id)

        server_schema = ServerUpdate(in_upgrade=True)
        server_schema = server_schema.rm_none_attrs()
        await crud_update_server(server_schema, server.id)

        # Make payment request and return it uri
        await r.set(f"upgrade_server:{server_id}", server_id, ex=60 * PAYMENT_TIME)
        await r.set(f"unupgraded_server:{server_id}", upgrade_vds.id)

        payment_data = await payment_request("upgrade", server_id, product_id)
        qrcode = await draw_qrcode(payment_data["payment_uri"])

        return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])
    else:
        return await t_error(request, 503, "We haven't available resources")
