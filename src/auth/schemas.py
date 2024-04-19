from pydantic import BaseModel, EmailStr


class Login(BaseModel):
    username: str
    password: str


class Register(BaseModel):
    username: str
    password: str
    captcha_id: int
    captcha_text: str


class ResetPassword(BaseModel):
    old_password: str
    new_password: str


class ResetEmail(BaseModel):
    email: EmailStr


class Recovery(BaseModel):
    username: str
    email: str


class Captcha(BaseModel):
    captcha_id: int
    captcha_text: str
