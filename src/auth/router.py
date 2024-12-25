from uuid import uuid4
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from src.config import REGISTRATION
from src.database import r, execute, fetchone, fetchall
from src.auth.utils import active_user
from src.display.utils import t_error


async def login(request: Request):
    form = await request.form()
    password = form.get("password")

    if not password:
        return await t_error(request, 400, "The password field is required")

    user = await fetchone("SELECT * FROM user WHERE password = ?", (password,))

    if not user:
        return await t_error(request, 401, "Invalid password")

    token = uuid4()
    await r.set(f"auth:{token}", user["id"], ex=86400)

    servers = await fetchall("SELECT * FROM server WHERE user_id = ?", (user["id"],))
    active_servers = [server for server in servers if server["is_active"]]
    url = '/' if not active_servers else "/dashboard"

    return RedirectResponse(url, status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=86400;"
    })


async def register(request: Request):
    if not REGISTRATION:
        return await t_error(request, 400, "Registration is disabled")

    form = await request.form()
    password1 = form.get("password1")
    password2 = form.get("password2")
    captcha_id = form.get("captcha_id")

    # Check password
    if not password1 or not password2 or not captcha_id:
        return await t_error(request, 400, "The fields password1, password2 and captcha_id are required")

    if len(password1) not in range(8, 21):
        return await t_error(request, 400, "The password length must be 8-20 characters")

    if password1 != password2:
        return await t_error(request, 400, "Passwords don't match")

    # Check captcha
    captcha_lock_id = await r.get(f"captcha:{captcha_id}")

    if not captcha_lock_id:
        return await t_error(request, 400, "Press the Register button within a minute")

    await r.delete(f"captcha:{captcha_id}")
    captcha_lock = await r.get(f"captcha_lock:{captcha_lock_id}")

    if captcha_lock:
        return await t_error(request, 400, "Wait a few seconds before clicking the Register button")

    # Check user
    user = await fetchone("SELECT * FROM user WHERE password = ?", (password1,))

    if user:
        return await t_error(request, 400, "User already exist")

    # User registration
    await execute("INSERT INTO user (password) VALUES (?)", (password1,))
    user = await fetchone("SELECT * FROM user WHERE password = ?", (password1,))

    token = uuid4()

    await r.set(f"auth:{token}", user["id"], ex=86400)

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

    if not old_password or not new_password:
        return await t_error(request, 400, "The fields old_password1 and new_password are required")

    if user["password"] != old_password:
        return await t_error(request, 403, "Invalid password")

    is_exist = await fetchone("SELECT * FROM user WHERE password = ?", (new_password,))

    if is_exist:
        return await t_error(request, 400, "User with this password already exist")

    await execute("UPDATE user SET password = ? WHERE id = ?", (new_password, user["id"]))

    token = uuid4()

    await r.set(f"auth:{token}", user["id"], ex=86400)

    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=86400;"
    })


router = [
    Route("/login", login, methods=["POST"]),
    Route("/register", register, methods=["POST"]),
    Route("/logout", logout, methods=["POST"]),
    Route("/reset_password", reset_password, methods=["POST"])
]
