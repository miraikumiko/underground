from starlette.authentication import requires, UnauthenticatedUser
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException
from underground.config import REGISTRATION
from underground.database import database
from underground.models import IsoImage, VDS, Node, Server
from underground.utils.payment import usd_to_xmr, payment_request
from underground.utils.server import vds_status
from underground.utils.display import templates, no_cache_headers, draw_qrcode


async def display_index(request: Request):
    user = request.user
    in_stock = {}
    server = None

    if not isinstance(user, UnauthenticatedUser):
        server = await database.fetch_one(Server.select().where(Server.c.user_id == user.id))
    else:
        user = None

    vdss = await database.fetch_all(VDS.select())
    nodes = await database.fetch_all(Node.select())

    for vds in vdss:
        for node in nodes:
            if vds.cores <= node.cores_available and vds.ram <= node.ram_available and vds.disk_size <= node.disk_size_available:
                in_stock[vds.id] = True
                break

            in_stock[vds.id] = False

    return templates.TemplateResponse(request, "index.html", {
        "user": user,
        "vdss": vdss,
        "in_stock": in_stock,
        "server": server
    })


async def display_login(request: Request):
    return templates.TemplateResponse(request, "login.html")


async def display_register(request: Request):
    if not REGISTRATION:
        raise HTTPException(400, "Registration is disabled")

    return templates.TemplateResponse(request, "register.html")


@requires("authenticated")
async def display_dashboard(request: Request):
    user = request.user
    servers = await database.fetch_all(Server.select().where(Server.c.user_id == user.id))
    statuses = []

    if not servers:
        return RedirectResponse('/', 301, no_cache_headers)

    for server in servers:
        node = await database.fetch_one(Node.select().where(Node.c.id == server.node_id))
        status = await vds_status(server.id, node.ip)

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


@requires("authenticated")
async def display_promo(request: Request):
    return templates.TemplateResponse(request, "promo.html")


@requires("authenticated")
async def display_checkout(request: Request):
    user = request.user
    vds_id = request.path_params.get("product_id")
    vds = await database.fetch_one(VDS.select().where(VDS.c.id == vds_id))
    course = request.app.state.XMR_COURSE
    amount = await usd_to_xmr(vds.price, course)
    payment_uri = await payment_request(user.id, amount)
    qrcode = await draw_qrcode(payment_uri)

    return templates.TemplateResponse(request, "checkout.html", {
        "uri": payment_uri,
        "qrcode": qrcode,
        "price": vds.price,
        "course": course
    })


@requires("authenticated")
async def display_install(request: Request):
    server_id = request.path_params.get("server_id")
    oss = await database.fetch_all(IsoImage.select())

    return templates.TemplateResponse(request, "install.html", {"server_id": server_id, "oss": oss})


@requires("authenticated")
async def display_vnc(request: Request):
    server_id = request.path_params.get("server_id")

    return templates.TemplateResponse(request, "vnc.html", {"server_id": server_id})


@requires("authenticated")
async def display_upgrade(request: Request):
    server_id = request.path_params.get("server_id")
    server = await database.fetch_one(Server.select().where(Server.c.id == server_id))
    server_vds = await database.fetch_one(VDS.select().where(VDS.c.id == server.vds_id))
    vdss = await database.fetch_all(VDS.select())
    vdss = [vds for vds in vdss if vds.id > server.vds_id]

    if not vdss:
        raise HTTPException(400, "Your VDS is already fully upgraded")

    return templates.TemplateResponse(request, "upgrade.html", {
        "server_vds_price": server_vds.price,
        "vdss": vdss,
        "server_id": server_id
    })


display_router = [
    Route("/", display_index, methods=["GET"]),
    Route("/login", display_login, methods=["GET"]),
    Route("/register", display_register, methods=["GET"]),
    Route("/dashboard", display_dashboard, methods=["GET"]),
    Route("/promo", display_promo, methods=["GET"]),
    Route("/checkout/{product_id:int}", display_checkout, methods=["GET"]),
    Route("/install/{server_id:int}", display_install, methods=["GET"]),
    Route("/vnc/{server_id:int}", display_vnc, methods=["GET"]),
    Route("/upgrademenu/{server_id:int}", display_upgrade, methods=["GET"])
]
