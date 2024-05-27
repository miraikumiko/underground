from pydantic import BaseModel


class NodeCreate(BaseModel):
    ip: str
    cores: int
    cores_available: int
    ram: int
    ram_available: int
    disk_type: str
    disk_size: int
    disk_size_available: int
    location: str


class NodeRead(BaseModel):
    id: int
    ip: str
    cores: int
    cores_available: int
    ram: int
    ram_available: int
    disk_type: str
    disk_size: int
    disk_size_available: int
    location: str


class NodeUpdate(BaseModel):
    cores_available: int = None
    ram_available: int = None
    disk_size_available: int = None
