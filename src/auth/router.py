from uuid import uuid4
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from src.config import REGISTRATION
from src.database import Database, r
from src.auth.utils import active_user
from src.display.utils import t_error

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login_form(request: Request, password: str = Form(...)):
    async with Database() as db:
        user = await db.fetchone("SELECT * FROM user WHERE password = ?", (password,))

    if user:
        token = uuid4()
        await r.set(f"auth:{token}", user[0], ex=86400)

        async with Database() as db:
            servers = await db.fetchall("SELECT * FROM server WHERE user_id = ?", (user[0],))

        active_servers = [server for server in servers if server[4]]
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

    async with Database() as db:
        user = await db.fetchone("SELECT * FROM user WHERE password = ?", (password,))

    if user:
        return await t_error(request, 400, "User already exist")

    async with Database() as db:
        await db.execute("INSERT INTO user (password) VALUES (?)", (password,))
        user = await db.fetchone("SELECT * FROM user WHERE password = ?", (password,))

    token = uuid4()

    await r.set(f"auth:{token}", user[0], ex=86400)

    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=86400;"
    })


@router.post("/logout")
async def logout(request: Request):
    _ = await active_user(request)

    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax;'
    })


@router.post("/reset-password")
async def reset_password_form(request: Request, old_password: str = Form(...), new_password: str = Form(...)):
    user = await active_user(request)

    if user[1] != old_password:
        return await t_error(request, 403, "Invalid password")

    async with Database() as db:
        is_exist = await db.fetchone("SELECT * FROM user WHERE password = ?", (new_password,))

        if is_exist:
            return await t_error(request, 400, "User already exist")

        await db.execute("UPDATE user SET password = ? WHERE id = ?", (new_password, user[0]))

    token = uuid4()

    await r.set(f"auth:{token}", user[0], ex=86400)

    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=86400;"
    })


@router.post("/delete-account")
async def delete_me_form(request: Request, password: str = Form(...)):
    user = await active_user(request)

    if user[1] != password:
        return await t_error(request, 403, "Invalid password")

    async with Database() as db:
        await db.execute("DELETE FROM server WHERE user_id = ?", (user[0],))
        await db.execute("DELETE FROM user WHERE id = ?", (user[0],))

    return RedirectResponse('/', status_code=301, headers={
        "content-type": "application/x-www-form-urlencoded",
        "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax;'
    })
