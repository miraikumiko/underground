from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from src.logger import logger
from src.user.models import User
from src.user.schemas import UserUpdate, UserDelete
from src.user.crud import crud_read_user, crud_update_user, crud_delete_user
from src.server.crud import crud_delete_servers
from src.auth.utils import password_helper, active_user

router = APIRouter(prefix="/api/user", tags=["users"])


@router.get("/me")
async def read_me(user: User = Depends(active_user)):
    del user.password
    return user


@router.patch("/me")
async def update_me(data: UserUpdate, user: User = Depends(active_user)):
    await crud_update_user(data, user.id)


@router.delete("/me")
async def delete_me(data: UserDelete, user: User = Depends(active_user)):
    if password_helper.verify_and_update(data.password, user.password)[0]:
        await crud_delete_servers(user.id)
        await crud_delete_user(user.id)

        return Response(status_code=204, headers={
            "content-type": "application/x-www-form-urlencoded",
            "set-cookie": 'fastapiusersauth=""; HttpOnly; Max-Age=0; Path=/; SameSite=lax; Secure'
        })
    else:
        raise HTTPException(status_code=401)
