from pydantic import BaseModel


class Pay(BaseModel):
    server_id: int
    month: int
