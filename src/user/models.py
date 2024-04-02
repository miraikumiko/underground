from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from src.models import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, index=True, default=True)
    is_superuser = Column(Boolean, nullable=False, index=True, default=False)
    is_verified = Column(Boolean, nullable=False, index=True, default=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    notifications = Column(Boolean, nullable=False, index=True, default=True)
    reset_password = Column(Boolean, nullable=False, index=True, default=True)
