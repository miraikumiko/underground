from random import randint
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from src.config import REGISTRATION
from src.database import r, fetchone, fetchall
from src.auth.utils import active_user, active_user_opt
from src.payment.utils import xmr_course, usd_to_xmr, payment_request
from src.server.utils import vds_status
from src.display.utils import templates, no_cache_headers, t_error, draw_qrcode


async def index_display(request: Request):
    user = await active_user_opt(request)
    server = None

    if user:
        server = await fetchone("SELECT * FROM server WHERE user_id = ?", (user["id"],))

    vdss = await fetchall("SELECT * FROM vds")

    return templates.TemplateResponse(request, "index.html", {
        "user": user,
        "vdss": vdss,
        "server": server
    })


async def login_display(request: Request):
    captcha_id = randint(10000, 99999)
    captcha_lock_id = randint(10000, 99999)

    await r.set(f"captcha:{captcha_id}", captcha_lock_id, ex=60)
    await r.set(f"captcha_lock:{captcha_lock_id}", 1, ex=2)

    return templates.TemplateResponse(request, "login.html", {"captcha_id": captcha_id})


async def register_display(request: Request):
    if not REGISTRATION:
        return await t_error(request, 400, "Registration is disabled")

    captcha_id = randint(10000, 99999)
    captcha_lock_id = randint(10000, 99999)

    await r.set(f"captcha:{captcha_id}", captcha_lock_id, ex=60)
    await r.set(f"captcha_lock:{captcha_lock_id}", 1, ex=4)

    return templates.TemplateResponse(request, "register.html", {"captcha_id": captcha_id})


async def dashboard_display(request: Request):
    user = await active_user(request)
    servers = await fetchall("SELECT * FROM server WHERE user_id = ?", (user["id"],))
    statuses = []

    if not servers:
        return RedirectResponse('/', 301, no_cache_headers)

    for server in servers:
        node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
        status = await vds_status(server["id"], node["ip"])

        if not status["ipv4"]:
            status["ipv4"] = '-'

        if not status["ipv6"]:
            status["ipv6"] = '-'

        statuses.append(status)

    servers_and_statuses = zip(servers, statuses)

    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "servers_and_statuses": servers_and_statuses
    })


async def promo_display(request: Request):
    _ = await active_user(request)

    return templates.TemplateResponse(request, "promo.html")


async def checkout_display(request: Request):
    user = await active_user(request)
    vds_id = request.path_params.get("product_id")
    vds = await fetchone("SELECT * FROM vds where id = ?", (vds_id,))
    amount = await usd_to_xmr(vds["price"])
    payment_uri = await payment_request(user["id"], amount)
    qrcode = await draw_qrcode(payment_uri)
    course = await xmr_course()

    return templates.TemplateResponse(request, "checkout.html", {
        "uri": payment_uri,
        "qrcode": qrcode,
        "price": vds["price"],
        "course": course
    })


async def install_display(request: Request):
    _ = await active_user(request)
    server_id = request.path_params.get("server_id")

    if not server_id:
        return await t_error(request, 400, "The field server_id is required")

    oss = await fetchall("SELECT * FROM os")

    return templates.TemplateResponse(request, "install.html", {"server_id": server_id, "oss": oss})


async def vnc_display(request: Request):
    _ = await active_user(request)
    server_id = request.path_params.get("server_id")

    if not server_id:
        return await t_error(request, 400, "The field server_id is required")

    return templates.TemplateResponse(request, "vnc.html", {"server_id": server_id})


async def upgrade_display(request: Request):
    _ = await active_user(request)
    server_id = request.path_params.get("server_id")

    if not server_id:
        return await t_error(request, 400, "The field server_id is required")

    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))
    server_vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))
    vdss = await fetchall("SELECT * FROM vds")
    vdss = [vds for vds in vdss if vds["id"] > server["vds_id"]]

    if not vdss:
        return await t_error(request, 400, "Your VDS is already fully upgraded")

    return templates.TemplateResponse(request, "upgrade.html", {
        "server_vds_price": server_vds["price"],
        "vdss": vdss,
        "server_id": server_id
    })


display_router = [
    Route("/", index_display, methods=["GET"]),
    Route("/login", login_display, methods=["GET"]),
    Route("/register", register_display, methods=["GET"]),
    Route("/dashboard", dashboard_display, methods=["GET"]),
    Route("/promo", promo_display, methods=["GET"]),
    Route("/checkout/{product_id:int}", checkout_display, methods=["GET"]),
    Route("/install/{server_id:int}", install_display, methods=["GET"]),
    Route("/vnc/{server_id:int}", vnc_display, methods=["GET"]),
    Route("/upgrademenu/{server_id:int}", upgrade_display, methods=["GET"])
]
