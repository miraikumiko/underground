from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from src.database import Database, r
from src.server.utils import request_vds
from src.auth.utils import active_user
from src.display.utils import t_error

router = APIRouter(prefix="/api/payment", tags=["payments"])


@router.post("/close")
async def close(request: Request):
    user = await active_user(request)
    payment_uri = await r.get(f"payment_uri:{user[0]}")

    if payment_uri:
        await r.delete(f"payment_uri:{user[0]}")

        return RedirectResponse('/', status_code=301)

    return await t_error(request, 400, "You haven't active payments")


@router.post("/promo")
async def promo(request: Request, code: str = Form(...)):
    user = await active_user(request)

    async with Database() as db:
        promo_code = await db.fetchone("SELECT * FROM promo WHERE code = ?", (code,))

    if not promo_code:
        return await t_error(request, 422, "Invalid promo code")

    await request_vds(promo_code[3], user, True)

    # Mark promo code as used
    async with Database() as db:
        await db.execute("DELETE FROM promo WHERE id = ?", (promo_code[0],))

    return RedirectResponse("/dashboard", status_code=301)
