from datetime import timedelta
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from src.database import Database, r
from src.config import REGISTRATION, VDS_DAYS, VDS_MAX_PAYED_DAYS, PAYMENT_TIME
from src.auth.utils import active_user, active_user_opt
from src.server.vds import vds_status
from src.server.utils import request_vds
from src.payment.payments import payment_request
from src.payment.utils import check_active_payment, check_payment_limit, xmr_course
from src.display.utils import templates, t_error, t_checkout, get_captcha_base64, draw_qrcode

router = APIRouter()


@router.get("/")
async def index(request: Request):
    user = await active_user_opt(request)

    if user:
        async with Database() as db:
            servers = await db.fetchall("SELECT * FROM server WHERE user_id = ?", (user[0],))

        active_servers = [server for server in servers if server[4]]
    else:
        active_servers = None

    course = await xmr_course()

    async with Database() as db:
        vdss = await db.fetchall("SELECT * FROM vds")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "course": course,
        "vdss": vdss,
        "servers": active_servers
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
async def change_password(request: Request):
    _ = await active_user(request)

    return templates.TemplateResponse("change-password.html", {"request": request})


@router.get("/delete-account")
async def delete_account(request: Request):
    _ = await active_user(request)

    return templates.TemplateResponse("delete-account.html", {"request": request})


@router.get("/dashboard")
async def dashboard(request: Request):
    user = await active_user(request)
    course = await xmr_course()

    async with Database() as db:
        servers = await db.fetchall("SELECT * FROM server WHERE user_id = ?", (user[0],))

    active_servers = [server for server in servers if server[4]]
    statuses = []

    if not active_servers:
        return RedirectResponse('/', status_code=301)

    for server in active_servers:
        async with Database() as db:
            node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))

        status = await vds_status(server[0], node[1])

        if not status["ipv4"]:
            status["ipv4"] = '-'

        if not status["ipv6"]:
            status["ipv6"] = '-'

        statuses.append(status)

    servers_and_statuses = zip(active_servers, statuses)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "course": course,
        "servers_and_statuses": servers_and_statuses
    })


@router.get("/promo")
async def promo(request: Request):
    _ = await active_user(request)

    return templates.TemplateResponse("promo.html", {"request": request})


@router.get("/faq")
async def faq(request: Request):
    user = await active_user_opt(request)
    active_servers = []
    course = await xmr_course()

    if user:
        async with Database() as db:
            servers = await db.fetchall("SELECT * FROM server WHERE user_id = ?", (user[0],))

        active_servers = [server for server in servers if server[4]]

    return templates.TemplateResponse("faq.html", {
        "request": request,
        "user": user,
        "course": course,
        "servers": active_servers
    })


@router.get("/install/{server_id}")
async def install(server_id: int, request: Request):
    _ = await active_user(request)

    return templates.TemplateResponse("install.html", {
        "request": request,
        "server_id": server_id
    })


@router.get("/vnc/{server_id}")
async def vnc(server_id: int, request: Request):
    _ = await active_user(request)

    return templates.TemplateResponse("vnc.html", {
        "request": request,
        "server_id": server_id
    })


@router.get("/buy/{product_id}")
async def buy(product_id: int, request: Request):
    user = await active_user(request)

    # Check if user have active payment
    cap = await check_active_payment(user[0])

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user[0])

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    server_id = await request_vds(product_id, user)

    # Make payment request and return it uri
    await r.set(f"inactive_server:{server_id}", server_id, ex=60 * PAYMENT_TIME)

    payment_data = await payment_request("buy", server_id)
    qrcode = await draw_qrcode(payment_data["payment_uri"])

    return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])


@router.get("/pay/{server_id}")
async def pay(server_id: int, request: Request):
    user = await active_user(request)

    # Check server
    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or server[8] != user[0]:
        return await t_error(request, 400, "Invalid server")
 
    # Check if user have active payment
    cap = await check_active_payment(user[0])

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user[0])

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    # Check expiring date
    if server[3] - server[2] > timedelta(days=VDS_MAX_PAYED_DAYS - VDS_DAYS):
        return await t_error(request, 400, f"You can't pay for more than {VDS_MAX_PAYED_DAYS} days")

    # Make payment request and return it uri
    payment_data = await payment_request("pay", server_id)
    qrcode = await draw_qrcode(payment_data["payment_uri"])

    return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])


@router.get("/upgrademenu/{server_id}")
async def upgrademenu(server_id: int, request: Request):
    _ = await active_user(request)

    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))
        vdss = await db.fetchall("SELECT * FROM vds")

    vdss = [vds for vds in vdss if vds[0] > server[6]]

    if not vdss:
        return await t_error(request, 400, "Your VDS is already fully upgraded")

    return templates.TemplateResponse("upgrade.html", {
        "request": request,
        "vdss": vdss,
        "server_id": server_id
    })


@router.get("/upgrade/{server_id}")
async def upgrade(server_id: int, product_id: int, request: Request):
    user = await active_user(request)

    # Check server
    async with Database() as db:
        server = await db.fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if not server or not server[4] or server[8] != user[0] or server[6] >= product_id:
        return await t_error(request, 400, "Invalid server")

    # Check if user have active payment
    cap = await check_active_payment(user[0])

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user[0])

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    # Validate product id
    async with Database() as db:
        upgrade_vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (product_id,))

    if not upgrade_vds:
        return await t_error(request, 400, "This product doesn't exist")

    # Check availability of resources
    async with Database() as db:
        node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))
        server_vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (server[6],))
        nodes = await db.fetchall(
            "SELECT * FROM node WHERE cores_available >= ? AND ram_available >= ? AND disk_size_available >= ?",
            (upgrade_vds[1], upgrade_vds[2], upgrade_vds[3])
        )

    if nodes:
        if node in nodes:
            async with Database() as db:
                await db.execute(
                    "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                    (
                        node[3] - upgrade_vds[1] + server_vds[1],
                        node[5] - upgrade_vds[2] + server_vds[2],
                        node[7] - upgrade_vds[3] + server_vds[3],
                        server[8]
                    )
                )
        else:
            dst_node = nodes[0]
            await r.set(f"node_to_migrate:{server_id}", dst_node[0])

            async with Database() as db:
                await db.execute(
                    "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                    (
                        dst_node[3] - upgrade_vds[1] + server_vds[1],
                        dst_node[5] - upgrade_vds[2] + server_vds[2],
                        dst_node[7] - upgrade_vds[3] + server_vds[3],
                        dst_node[0]
                    )
                )

        async with Database() as db:
            await db.execute("UPDATE server SET in_upgrade = 1 WHERE id = ?", (server[0],))

        # Make payment request and return it uri
        await r.set(f"upgrade_server:{server_id}", server_id, ex=60 * PAYMENT_TIME)
        await r.set(f"unupgraded_server:{server_id}", upgrade_vds[0])

        payment_data = await payment_request("upgrade", server_id, product_id)
        qrcode = await draw_qrcode(payment_data["payment_uri"])

        return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])
    else:
        return await t_error(request, 503, "We haven't available resources")
