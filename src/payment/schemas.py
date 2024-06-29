from pydantic import BaseModel


class Buy(BaseModel):
    vps_id: int


class Pay(BaseModel):
    server_id: int


class Upgrade(BaseModel):
    server_id: int
    vps_id: int


class QRCode(BaseModel):
    uri: str
