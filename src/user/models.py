from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON
)
from src.models import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    settings = Column(JSON, nullable=False)
