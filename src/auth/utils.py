from fastapi import Request, HTTPException
from src.database import r
from src.user.crud import crud_read_user


async def active_user(request: Request):
    if "auth" in request.cookies:
        token = request.cookies["auth"]
    else:
        raise HTTPException(status_code=401)

    user_id = await r.get(f"auth:{token}")

    if user_id is not None:
        user = await crud_read_user(int(user_id))

        if user.is_active:
            return user
        else:
            raise HTTPException(status_code=401)
    else:
        raise HTTPException(status_code=401)


async def verified_user(request: Request):
    if "auth" in request.cookies:
        token = request.cookies["auth"]
    else:
        raise HTTPException(status_code=401)

    user_id = await r.get(f"auth:{token}")

    if user_id is not None:
        user = await crud_read_user(int(user_id))

        if user.is_active and user.is_verified:
            return user
        else:
            raise HTTPException(status_code=401)
    else:
        raise HTTPException(status_code=401)


async def admin(request: Request):
    if "auth" in request.cookies:
        token = request.cookies["auth"]
    else:
        raise HTTPException(status_code=401)

    user_id = await r.get(f"auth:{token}")

    if user_id is not None:
        user = await crud_read_user(int(user_id))

        if user.is_active and user.is_superuser and user.is_verified:
            return user
        else:
            raise HTTPException(status_code=401)
    else:
        raise HTTPException(status_code=401)
