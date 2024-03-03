from fastapi import APIRouter, HTTPException
from src.logger import logger
from src.user.schemas import UserSettingsCreate
from src.user.crud import crud_create_user, crud_create_user_settings
from src.auth.utils import users, auth_backend
from src.user.schemas import UserCreate, UserRead, UserUpdate

users_router = users.get_users_router(UserRead, UserUpdate)
auth_router = users.get_auth_router(auth_backend)
reset_password_router = users.get_reset_password_router()
verify_router = users.get_verify_router(UserRead)


register_router = APIRouter()


@register_router.post("/register", status_code=201)
async def register_user(data: UserCreate):
    try:
        user_id = await crud_create_user(data)

        user_settings = UserSettingsCreate(user_id=user_id)

        await crud_create_user_settings(user_settings)

        return {"user_id": user_id}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail=str(e))
