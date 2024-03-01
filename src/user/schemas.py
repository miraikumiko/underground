from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUserCreate, BaseUser, BaseUserUpdate


class UserCreate(BaseUserCreate):
    password: str
    hashed_password: str = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserRead(BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserUpdate(BaseUserUpdate):
    email: EmailStr
    password: str
    hashed_password: str = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserDelete(BaseModel):
    id: int


class UserSettingsCreate(BaseModel):
    user_id: int
    notifications: bool = True
    reset_password: bool = True


class UserSettingsRead(BaseModel):
    id: int
    user_id: int
    notifications: bool
    reset_password: bool


class UserSettingsUpdate(BaseModel):
    id: int
    user_id: int
    notifications: bool
    reset_password: bool


class UserSettingsDelete(BaseModel):
    id: int
