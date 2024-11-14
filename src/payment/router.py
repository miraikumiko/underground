from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, StreamingResponse
from src.database import r
from src.config import PRODUCTS
from src.payment.schemas import QRCode
from src.payment.payments import payment_request
from src.payment.utils import check_active_payment, check_payment_limit, draw_qrcode, xmr_course
from src.server.crud import crud_read_server
from src.node.crud import crud_read_nodes
from src.user.models import User
from src.auth.utils import active_user
from src.display.utils import templates

router = APIRouter(prefix="/api/payment", tags=["payments"])


@router.get("/upgrade/{server_id}")
async def upgrade(
    server_id: int, product_id: int,
    request: Request, user: User = Depends(active_user)
):
    # Check auth
    if user is None:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Unauthorized",
            "msg2": "Please login"
        })

    # Check server
    server = await crud_read_server(server_id)

    if server is None or server.user_id != user.id or server.vps_id >= product_id:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "Invalid server"
        })

    # Check if user have active payment
    cap = await check_active_payment(user.id)

    if cap is not None:
        return templates.TemplateResponse("checkout.html", {
            "request": request,
            "qrcode": cap["qrcode"],
            "uri": cap["payment_uri"],
            "ttl": cap["ttl"]
        })

    # Check user's payment limit
    cpl = await check_payment_limit(user.id)

    if cpl:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "You can make only 3 payment requests per day"
        })

    # Validate product id
    if not [vps_id for vps_id in PRODUCTS["vps"] if int(vps_id) == product_id]:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "This product doesn't exist"
        })

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

    # Make payment request and return it uri
    payment_data = await payment_request("upgrade", server_id, product_id)
    qrc = await draw_qrcode(payment_data["payment_uri"])

    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "qrcode": qrc,
        "uri": payment_data["payment_uri"],
        "ttl": payment_data["ttl"]
    })


@router.post("/close")
async def close(request: Request, user: User = Depends(active_user)):
    payment_uri = await r.get(f"payment_uri:{user.id}")

    if payment_uri is not None:
        await r.delete(f"payment_uri:{user.id}")

        return RedirectResponse('/', status_code=301)

    return templates.TemplateResponse("error.html", {
        "request": request,
        "msg1": "Bad Request",
        "msg2": "You haven't active payments"
    })


@router.post("/qrcode")
async def qrcode(data: QRCode, _: User = Depends(active_user)):
    qrc = await draw_qrcode(data.uri)

    return StreamingResponse(qrc, media_type="image/png")


@router.get("/products")
async def products():
    return PRODUCTS


@router.get("/course")
async def course():
    return await xmr_course()
