from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)
from src.logger import logger
from src.user.models import User
from src.user.schemas import UserUpdate
from src.user.crud import (
    crud_read_user,
    crud_update_user,
    crud_delete_user
)
from src.auth.utils import active_user, admin

router = APIRouter(prefix="/api/user", tags=["users"])


@router.get("/me")
async def read_me(user: User = Depends(active_user)):
    try:
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.patch("/update/me")
async def update_me(data: UserUpdate, user: User = Depends(active_user)):
    try:
        await crud_update_user(data, user.id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.delete("/delete/me")
async def delete_me(user: User = Depends(active_user)):
    try:
        await crud_delete_user(user.id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.get("/{user_id}")
async def read_user(user_id: int, _: User = Depends(admin)):
    try:
        user = await crud_read_user(user_id)

        if user is None:
            raise ValueError(f"User with id {user_id} doesn't exist")

        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.patch("/update/{user_id}")
async def update_user(user_id: int, data: UserUpdate, _: User = Depends(admin)):
    try:
        await crud_update_user(data, user_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)


@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, _: User = Depends(admin)):
    try:
        await crud_delete_user(user_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)
