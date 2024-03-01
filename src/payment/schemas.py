from pydantic import BaseModel


class PaymentCreate(BaseModel):
    user_id: int
    server_id: int
    active_server_id: int = None
    payment_id: int
    amount: int
    month: int
    active: bool = True


class PaymentRead(BaseModel):
    id: int = None
    user_id: int
    server_id: int
    active_server_id: int = None
    payment_id: int
    amount: int
    month: int
    active: bool


class PaymentUpdate(BaseModel):
    id: int
    payment_id: int
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
