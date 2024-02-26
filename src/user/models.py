from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import (
    Column,
    CheckConstraint,
    Integer,
    Boolean,
    String,
    JSON,
    ForeignKey
)
from src.models import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    notifications = Column(Boolean, nullable=False, unique=True, index=True, default=True)
    reset_password = Column(Boolean, nullable=False, unique=True, index=True, default=True)
