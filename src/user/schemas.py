from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str
    hashed_password: str = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None
    hashed_password: str = None
    is_active: bool = None
    is_superuser: bool = None
    is_verified: bool = None


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
    notifications: bool
    reset_password: bool


class UserSettingsDelete(BaseModel):
    id: int
