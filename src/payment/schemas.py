from pydantic import BaseModel


class PaymentCreate(BaseModel):
    id: int
    user_id: int
    server_id: int
    active_server_id: int = None
    amount: int
    month: int
    active: bool = True


class PaymentRead(BaseModel):
    id: int = None
    user_id: int
    server_id: int
    active_server_id: int = None
    amount: int
    month: int
    active: bool


class PaymentUpdate(BaseModel):
    active: bool


class PaymentDelete(BaseModel):
    id: int


class DiscountCreate(BaseModel):
    user_id: int
    discount: int


class DiscountRead(BaseModel):
    id: int = None
    user_id: int
    discount: int


class DiscountUpdate(BaseModel):
    id: int
    discount: int


class DiscountDelete(BaseModel):
    id: int
