from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from src.database import r, execute, fetchone
from src.auth.utils import active_user
from src.payment.utils import request_vds
from src.display.utils import t_error


async def close(request: Request):
    user = await active_user(request)
    payment_uri = await r.get(f"payment_uri:{user['id']}")

    if payment_uri:
        await r.delete(f"payment_uri:{user['id']}")

        return RedirectResponse('/', status_code=301)

    return await t_error(request, 400, "You haven't active payments")


async def promo(request: Request):
    user = await active_user(request)
    form = await request.form()
    code = form.get("code")

    if not code:
        return await t_error(request, 400, "The code field is required")

    promo_code = await fetchone("SELECT * FROM promo WHERE code = ?", (code,))

    if not promo_code:
        return await t_error(request, 422, "Invalid promo code")

    await request_vds(promo_code["vds_id"], user, True)

    # Mark promo code as used
    await execute("DELETE FROM promo WHERE id = ?", (promo_code["id"],))

    return RedirectResponse("/dashboard", status_code=301)


router = [
    Route("/close", close, methods=["POST"]),
    Route("/promo", promo, methods=["POST"])
]
