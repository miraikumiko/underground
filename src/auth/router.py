from uuid import uuid4
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from src.config import REGISTRATION
from src.database import r
from src.crud import crud_create, crud_read, crud_update, crud_delete
from src.auth.models import User
from src.auth.utils import active_user
from src.server.crud import crud_read_servers, crud_delete_servers
from src.display.utils import t_error

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login_form(request: Request, password: str = Form(...)):
    user = await crud_read(User, User.password, password)

    if user:
        token = uuid4()
        await r.set(f"auth:{token}", user.id, ex=86400)

        servers = await crud_read_servers(user.id)
        active_servers = [server for server in servers if server.is_active]
        url = '/' if not active_servers else "/dashboard"

        return RedirectResponse(url, status_code=301, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=86400;"
        })
    else:
        return await t_error(request, 401, "Invalid password")


@router.post("/register")
async def register_form(request: Request, password: str = Form(...), captcha_id: str = Form(...), captcha_text: str = Form(...)):
    if not REGISTRATION:
        return await t_error(request, 400, "Registration is disabled")

    captcha = await r.get(f"captcha:{captcha_id}")
    await r.delete(f"captcha:{captcha_id}")

    if not captcha:
        return await t_error(request, 400, "Captcha was expired")

    if captcha != captcha_text:
        return await t_error(request, 400, "Captcha didn't match")

    if len(password) not in range(8, 33):
        return await t_error(request, 400, "The password length must be between 8 and 32 characters")

    user = await crud_read(User, attr1=User.password, attr2=password)

    if user:
        return await t_error(request, 400, "User already exist")

    user_id = await crud_create(User, {"password": password})
    token = uuid4()

    await r.set(f"auth:{token}", user_id, ex=86400)

    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=86400;"
    })


@router.post("/logout")
async def logout(_: User = Depends(active_user)):
    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax;'
    })


@router.post("/reset-password")
async def reset_password_form(
    request: Request,
    old_password: str = Form(...), new_password: str = Form(...),
    user: User = Depends(active_user)
):
    if user.password == old_password:
        token = uuid4()

        await crud_update(User, {"password": new_password}, User.id, user.id)
        await r.set(f"auth:{token}", user.id, ex=86400)

        return RedirectResponse('/', status_code=301, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=86400;"
        })
    else:
        return await t_error(request, 403, "Invalid password")


@router.post("/delete-account")
async def delete_me_form(request: Request, password: str = Form(...), user: User = Depends(active_user)):
    if user.password == password:
        await crud_delete_servers(user.id)
        await crud_delete(User, User.id, user.id)

        return RedirectResponse('/', status_code=301, headers={
            "content-type": "application/x-www-form-urlencoded",
            "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax;'
        })
    else:
        return await t_error(request, 403, "Invalid password")
