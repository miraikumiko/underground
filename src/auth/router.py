from uuid import uuid4
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import Response, RedirectResponse
from src.config import REGISTRATION
from src.database import r
from src.crud import crud_read
from src.auth.utils import password_helper, active_user
from src.user.models import User
from src.user.schemas import UserCreate, UserUpdate
from src.user.crud import crud_create_user, crud_update_user, crud_delete_user
from src.server.crud import crud_read_servers, crud_delete_servers
from src.display.utils import templates

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login_form(request: Request, username: str = Form(...), password: str = Form(...)):
    user = await crud_read(User, attr1=User.username, attr2=username)

    if user is not None and password_helper.verify_and_update(password, user.password)[0]:
        token = uuid4()
        await r.set(f"auth:{token}", user.id, ex=86400)

        servers = await crud_read_servers(user.id)
        servers = [server for server in servers if server.is_active]
        url = '/' if not servers else "/dashboard"

        return RedirectResponse(url, status_code=301, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Secure; Max-Age=86400"
        })
    else:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Unauthorized",
            "msg2": "Invalid login or password"
        })


@router.post("/register")
async def register_form(
    request: Request,
    username: str = Form(...), password: str = Form(...),
    captcha_id: str = Form(...), captcha_text: str = Form(...)
):
    if not REGISTRATION:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "Registration is disabled"
        })

    captcha = await r.get(f"captcha:{captcha_id}")
    await r.delete(f"captcha:{captcha_id}")

    if captcha is None:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "Captcha was expired"
        })

    if captcha != captcha_text:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "Captcha didn't match"
        })

    if len(username) not in range(21):
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "Username must be up to 20 characters"
        })

    if not username.isalnum():
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "Username must be contain only letters and numbers"
        })

    if len(password) not in range(51):
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "Password must be up to 50 characters"
        })

    user = await crud_read(User, attr1=User.username, attr2=username)

    if user is None:
        user = UserCreate(
            username=username, password=password_helper.hash(password)
        )
        user_id = await crud_create_user(user)
        token = uuid4()

        await r.set(f"auth:{token}", user_id, ex=86400)

        return RedirectResponse('/', status_code=301, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Secure; Max-Age=86400"
        })
    else:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Bad Request",
            "msg2": "User already exist"
        })


@router.post("/logout")
async def logout(_: User = Depends(active_user)):
    return RedirectResponse('/', status_code=301, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure'
    })


@router.post("/reset-password")
async def reset_password_form(
    old_password: str = Form(...), new_password: str = Form(...),
    user: User = Depends(active_user)
):
    if password_helper.verify_and_update(old_password, user.password)[0]:
        schema = UserUpdate()
        schema.password = password_helper.hash(new_password)
        token = uuid4()

        await crud_update_user(schema, user.id)
        await r.set(f"auth:{token}", user.id, ex=86400)

        return RedirectResponse('/', status_code=301, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": f"auth={token}; HttpOnly; Path=/; SameSite=lax; Secure; Max-Age=86400"
        })
    else:
        return Response(status_code=401)


@router.post("/delete-account")
async def delete_me_form(request: Request, password: str = Form(...), user: User = Depends(active_user)):
    if password_helper.verify_and_update(password, user.password)[0]:
        await crud_delete_servers(user.id)
        await crud_delete_user(user.id)

        return RedirectResponse('/', status_code=301, headers={
            "content-type": "application/x-www-form-urlencoded",
            "set-cookie": 'auth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure'
        })
    else:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "msg1": "Forbidden",
            "msg2": "Invalid password"
        })
