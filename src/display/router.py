from random import randint
from datetime import datetime, timedelta
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from src.config import REGISTRATION, VDS_DAYS, VDS_MAX_PAYED_DAYS, PAYMENT_TIME
from src.database import r, execute, fetchone, fetchall
from src.auth.utils import active_user, active_user_opt
from src.payment.utils import xmr_course, check_active_payment, check_payment_limit, payment_request, request_vds
from src.server.utils import vds_status
from src.display.utils import templates, t_error, t_checkout, draw_qrcode


async def index_display(request: Request):
    user = await active_user_opt(request)
    active_servers = []

    if user:
        servers = await fetchall("SELECT * FROM server WHERE user_id = ?", (user["id"],))
        active_servers = [server for server in servers if server["is_active"]]

    course = await xmr_course()
    vdss = await fetchall("SELECT * FROM vds")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "course": course,
        "vdss": vdss,
        "servers": active_servers
    })


async def login_display(request: Request):
    captcha_id = randint(10000, 99999)
    captcha_lock_id = randint(10000, 99999)

    await r.set(f"captcha:{captcha_id}", captcha_lock_id, ex=60)
    await r.set(f"captcha_lock:{captcha_lock_id}", 1, ex=2)

    return templates.TemplateResponse("login.html", {"request": request, "captcha_id": captcha_id})


async def register_display(request: Request):
    if not REGISTRATION:
        return await t_error(request, 400, "Registration is disabled")

    captcha_id = randint(10000, 99999)
    captcha_lock_id = randint(10000, 99999)

    await r.set(f"captcha:{captcha_id}", captcha_lock_id, ex=60)
    await r.set(f"captcha_lock:{captcha_lock_id}", 1, ex=4)

    return templates.TemplateResponse("register.html", {"request": request, "captcha_id": captcha_id})


async def dashboard_display(request: Request):
    user = await active_user(request)
    course = await xmr_course()
    servers = await fetchall("SELECT * FROM server WHERE user_id = ?", (user["id"],))
    active_servers = [server for server in servers if server["is_active"]]
    statuses = []

    if not active_servers:
        return RedirectResponse('/', status_code=301)

    for server in active_servers:
        node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
        status = await vds_status(server["id"], node["ip"])

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


async def promo_display(request: Request):
    _ = await active_user(request)

    return templates.TemplateResponse("promo.html", {"request": request})


async def install_display(request: Request):
    _ = await active_user(request)
    server_id = request.path_params.get("server_id")

    if not server_id:
        return await t_error(request, 400, "The field server_id is required")

    oss = await fetchall("SELECT * FROM os")

    return templates.TemplateResponse("install.html", {
        "request": request,
        "server_id": server_id,
        "oss": oss
    })


async def vnc_display(request: Request):
    _ = await active_user(request)
    server_id = request.path_params.get("server_id")

    if not server_id:
        return await t_error(request, 400, "The field server_id is required")

    return templates.TemplateResponse("vnc.html", {
        "request": request,
        "server_id": server_id
    })


async def buy_display(request: Request):
    user = await active_user(request)
    product_id = request.path_params.get("product_id")

    if not product_id:
        return await t_error(request, 400, "The field product_id is required")

    # Check if user have active payment
    cap = await check_active_payment(user["id"])

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user["id"])

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    server_id = await request_vds(product_id, user)

    # Make payment request and return it uri
    await r.set(f"inactive_server:{server_id}", server_id, ex=60 * PAYMENT_TIME)

    payment_data = await payment_request("buy", server_id)
    qrcode = await draw_qrcode(payment_data["payment_uri"])

    return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])


async def pay_display(request: Request):
    user = await active_user(request)
    server_id = request.path_params.get("server_id")

    if not server_id:
        return await t_error(request, 400, "The field server_id is required")

    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    # Check server
    if not server or server["user_id"] != user["id"]:
        return await t_error(request, 400, "Invalid server")
 
    # Check if user have active payment
    cap = await check_active_payment(user["id"])

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user["id"])

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    # Check expiring date
    if datetime.strptime(server["end_at"], "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(server["start_at"], "%Y-%m-%d %H:%M:%S.%f") > timedelta(days=VDS_MAX_PAYED_DAYS - VDS_DAYS):
        return await t_error(request, 400, f"You can't pay for more than {VDS_MAX_PAYED_DAYS} days")

    # Make payment request and return it uri
    payment_data = await payment_request("pay", server_id)
    qrcode = await draw_qrcode(payment_data["payment_uri"])

    return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])


async def upgrademenu_display(request: Request):
    _ = await active_user(request)
    server_id = request.path_params.get("server_id")

    if not server_id:
        return await t_error(request, 400, "The field server_id is required")

    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))
    vdss = await fetchall("SELECT * FROM vds")
    vdss = [vds for vds in vdss if vds["id"] > server["vds_id"]]

    if not vdss:
        return await t_error(request, 400, "Your VDS is already fully upgraded")

    return templates.TemplateResponse("upgrade.html", {
        "request": request,
        "vdss": vdss,
        "server_id": server_id
    })


async def upgrade_display(request: Request):
    user = await active_user(request)
    server_id = request.query_params.get("server_id")
    product_id = request.query_params.get("product_id")

    if not server_id or not product_id:
        return await t_error(request, 400, "The fields server_id and product_id are required")

    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    # Check server
    if not server or not server["is_active"] or server["user_id"] != user["id"] or server["vds_id"] >= product_id:
        return await t_error(request, 400, "Invalid server")

    # Check if user have active payment
    cap = await check_active_payment(user["id"])

    if cap:
        return await t_checkout(request, cap["qrcode"], cap["payment_uri"], cap["ttl"])

    # Check user's payment limit
    cpl = await check_payment_limit(user["id"])

    if cpl:
        return await t_error(request, 400, "You can make only 3 payment requests per day")

    # Validate product id
    upgrade_vds = await fetchone("SELECT * FROM vds WHERE id = ?", (product_id,))

    if not upgrade_vds:
        return await t_error(request, 400, "This product doesn't exist")

    # Check availability of resources
    node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
    server_vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))
    nodes = await fetchall(
        "SELECT * FROM node WHERE cores_available >= ? AND ram_available >= ? AND disk_size_available >= ?",
        (upgrade_vds["cores"], upgrade_vds["ram"], upgrade_vds["disk_size"])
    )

    if nodes:
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
        else:
            dst_node = nodes[0]
            await r.set(f"node_to_migrate:{server_id}", dst_node["id"])

            await execute(
                "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                (
                    dst_node["cores_available"] - upgrade_vds["cores"] + server_vds["cores"],
                    dst_node["ram_available"] - upgrade_vds["ram"] + server_vds["ram"],
                    dst_node["disk_size_available"] - upgrade_vds["disk_size"] + server_vds["disk_size"],
                    dst_node["id"]
                )
            )

        await execute("UPDATE server SET in_upgrade = 1 WHERE id = ?", (server["id"],))

        # Make payment request and return it uri
        await r.set(f"upgrade_server:{server_id}", server_id, ex=60 * PAYMENT_TIME)
        await r.set(f"unupgraded_server:{server_id}", upgrade_vds["id"])

        payment_data = await payment_request("upgrade", server["id"], upgrade_vds["id"])
        qrcode = await draw_qrcode(payment_data["payment_uri"])

        return await t_checkout(request, qrcode, payment_data["payment_uri"], payment_data["ttl"])
    else:
        return await t_error(request, 503, "We haven't available resources")


display_router = [
    Route("/", index_display, methods=["GET"]),
    Route("/login", login_display, methods=["GET"]),
    Route("/register", register_display, methods=["GET"]),
    Route("/dashboard", dashboard_display, methods=["GET"]),
    Route("/promo", promo_display, methods=["GET"]),
    Route("/install/{server_id:int}", install_display, methods=["GET"]),
    Route("/vnc/{server_id:int}", vnc_display, methods=["GET"]),
    Route("/buy/{product_id:int}", buy_display, methods=["GET"]),
    Route("/pay/{server_id:int}", pay_display, methods=["GET"]),
    Route("/upgrademenu/{server_id:int}", upgrademenu_display, methods=["GET"]),
    Route("/upgrade/{server_id:int}", upgrade_display, methods=["GET"])
]
