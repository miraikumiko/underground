from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from fastapi.responses import Response
from src.crud import crud_read
from src.logger import logger
from src.user.models import User
from src.user.schemas import UserSettingsCreate
from src.user.crud import crud_create_user, crud_create_user_settings
from src.auth.password import password_helper
from src.auth.utils import users, get_redis_strategy, active_user
from src.user.schemas import UserCreate, UserRead

reset_password_router = users.get_reset_password_router()
verify_router = users.get_verify_router(UserRead)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(username: str, password: str):
    try:
        user = await crud_read(User, attr1=User.username, attr2=username)

        if password_helper.verify_and_update(password, user.hashed_password)[0]:
            token = await get_redis_strategy().write_token(user)

            return Response(status_code=204, headers={
                "access-control-allow-origin": "http://127.0.0.1:8000",
                "Content-Type": "application/x-www-form-urlencoded",
                "set-cookie": f"fastapiusersauth={token}; HttpOnly; Path=/; SameSite=lax; Secure"
            })
        else:
            raise HTTPException(status_code=400, detail="Invalid password")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=400)


@router.post("/logout")
async def logout(_: User = Depends(active_user)):
    try:
        return Response(status_code=204, headers={
            "access-control-allow-origin": "http://127.0.0.1:8000",
            "Content-Type": "application/x-www-form-urlencoded",
            "set-cookie": 'fastapiusersauth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure'
        })
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=400)


@router.post("/register", status_code=201)
async def register(data: UserCreate):
    try:
        user_id = await crud_create_user(data)
        user_settings = UserSettingsCreate(user_id=user_id)
        await crud_create_user_settings(user_settings)

        return {"user_id": user_id}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=400)
