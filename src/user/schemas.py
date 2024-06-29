from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    is_active: bool = True


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool


class UserUpdate(BaseModel):
    password: str = None


class UserDelete(BaseModel):
    password: str
