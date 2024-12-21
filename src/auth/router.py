from uuid import uuid4
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from src.config import REGISTRATION
from src.database import Database, r
from src.auth.utils import active_user
from src.display.utils import t_error


async def login(request: Request):
    form = await request.form()
    password = form.get("password")

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


async def register(request: Request):
    if not REGISTRATION:
        return await t_error(request, 400, "Registration is disabled")

    form = await request.form()
    password = form.get("password")
    captcha_id = form.get("captcha_id")
    captcha_text = form.get("captcha_text")

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


async def logout(request: Request):
    _ = await active_user(request)

    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax;'
    })


async def reset_password(request: Request):
    user = await active_user(request)
    form = await request.form()
    old_password = form.get("old_password")
    new_password = form.get("new_password")

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


async def delete_account(request: Request):
    user = await active_user(request)
    form = await request.form()
    password = form.get("password")

    if user[1] != password:
        return await t_error(request, 403, "Invalid password")

    async with Database() as db:
        await db.execute("DELETE FROM server WHERE user_id = ?", (user[0],))
        await db.execute("DELETE FROM user WHERE id = ?", (user[0],))

    return RedirectResponse('/', status_code=301, headers={
        "content-type": "application/x-www-form-urlencoded",
        "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax;'
    })


router = [
    Route("/login", login, methods=["POST"]),
    Route("/register", register, methods=["POST"]),
    Route("/logout", logout, methods=["POST"]),
    Route("/reset_password", reset_password, methods=["POST"]),
    Route("/delete_account", delete_account, methods=["POST"])
]
