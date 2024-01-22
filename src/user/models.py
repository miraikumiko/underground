from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import (
    Column,
    Integer,
    String
)
from src.models import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
