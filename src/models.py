from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __init__(self, data, **kw: any):
        super().__init__(**kw)
        for key, value in data.items():
            setattr(self, key, value)
