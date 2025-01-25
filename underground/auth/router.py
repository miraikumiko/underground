from uuid import uuid4
from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException
from underground.config import REGISTRATION
from underground.database import execute, fetchone, fetchall
from underground.display.utils import no_cache_headers


async def login(request: Request):
    form = await request.form()
    password = form.get("password")

    if not password:
        raise HTTPException(400, "The field password is required")

    # Check password
    user = await fetchone("SELECT * FROM users WHERE password = ?", (password,))

    if not user:
        raise HTTPException(401, "Invalid password")

    # Create auth token
    while True:
        token = str(uuid4())
        token_exists = await fetchone("SELECT * FROM users WHERE token = ?", (token,))

        if not token_exists:
            await execute("UPDATE user SET token = ? WHERE id = ?", (token, user["id"]))
            break

    # Login
    server = await fetchone("SELECT * FROM server WHERE user_id = ?", (user["id"],))

    return RedirectResponse("/dashboard" if server else '/', 301, {
        "Content-Type": "application/x-www-form-urlencoded",
        "Set-Cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=2592000"
    } | no_cache_headers)


async def register(request: Request):
    if not REGISTRATION:
        raise HTTPException(403, "Registration is disabled")

    form = await request.form()
    password1 = form.get("password1")
    password2 = form.get("password2")

    # Check password
    if not password1 or not password2:
        raise HTTPException(400, "The fields password1 and password2 are required")

    if len(password1) not in range(8, 21):
        raise HTTPException(400, "The password length must be 8-20 characters")

    if password1 != password2:
        raise HTTPException(400, "Passwords don't match")

    # Check user
    user = await fetchone("SELECT * FROM users WHERE password = ?", (password1,))

    if user:
        raise HTTPException(409, "User already exist")

    # Create auth token
    while True:
        token = str(uuid4())
        token_exists = await fetchone("SELECT * FROM users WHERE token = ?", (token,))

        if not token_exists:
            # Registration
            await execute("INSERT INTO user (password, token) VALUES (?, ?)", (password1, token))
            break

    return RedirectResponse('/', 301, {
        "Content-Type": "application/x-www-form-urlencoded",
        "Set-Cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Max-Age=2592000"
    })


@requires("authenticated")
async def logout(request: Request):
    return RedirectResponse('/', 301, {
        "Content-Type": "application/x-www-form-urlencoded",
        "Set-Cookie": 'auth=; HttpOnly; Path=/; SameSite=lax; Max-Age=0'
    })


auth_router = [
    Route("/login", login, methods=["POST"]),
    Route("/register", register, methods=["POST"]),
    Route("/logout", logout, methods=["POST"])
]
