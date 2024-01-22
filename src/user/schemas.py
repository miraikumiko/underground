from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


class UserCreate(BaseUserCreate):
    email: str
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(BaseUserUpdate):
    email: str
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserRead(BaseUser[int]):
    id: int
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
