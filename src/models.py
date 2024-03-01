from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)
