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
    user_id: int
    server_id: int
    active_server_id: int = None
    payment_id: int
    amount: int
    month: int
    active: bool


class PaymentUpdate(BaseModel):
    payment_id: int
    active: bool


class PaymentDelete(BaseModel):
    id: int
