from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import EmailStr


class UserCreate(BaseUserCreate):
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(BaseUserUpdate):
    email: EmailStr
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserRead(BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool
