from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from src.database import r
from src.payment.schemas import PromoUpdate
from src.payment.crud import crud_read_promo, crud_update_promo
from src.server.utils import request_vps
from src.user.models import User
from src.auth.utils import active_user
from src.display.utils import t_error

router = APIRouter(prefix="/api/payment", tags=["payments"])


@router.post("/close")
async def close(request: Request, user: User = Depends(active_user)):
    payment_uri = await r.get(f"payment_uri:{user.id}")

    if payment_uri is not None:
        await r.delete(f"payment_uri:{user.id}")

        return RedirectResponse('/', status_code=301)

    return await t_error(request, 400, "You haven't active payments")


@router.post("/promo")
async def promo(request: Request, code: str = Form(...), user: User = Depends(active_user)):
    promo_code = await crud_read_promo(code)

    if promo_code is not None:
        if not promo_code.used:
            await request_vps(promo_code.vps_id, user, True)

            # Mark promo code as used
            promo_schema = PromoUpdate(used=True)
            await crud_update_promo(promo_schema, promo_code.id)

            return RedirectResponse("/dashboard", status_code=301)
        else:
            return await t_error(request, 400, "This promo code has been used")
    else:
        return await t_error(request, 422, "Invalid promo code")
