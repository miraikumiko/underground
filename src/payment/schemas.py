from pydantic import BaseModel


class Buy(BaseModel):
    vps_id: int


class Pay(BaseModel):
    server_id: int


class Upgrade(BaseModel):
    server_id: int
    vps_id: int


class PromoCreate(BaseModel):
    code: str
    used: bool = False
    vps_id: int = 1
    days: int = 31


class PromoRead(BaseModel):
    id: int
    code: str
    used: bool
    vps_id: int
    days: int


class PromoUpdate(BaseModel):
    used: bool


class QRCode(BaseModel):
    uri: str
