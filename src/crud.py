from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy import ColumnElement
from src.database import async_session_maker


async def crud_create(model, schema: BaseModel) -> int:
    async with async_session_maker() as session:
        async with session.begin():
            obj = model(schema.model_dump())

            session.add(obj)
            await session.commit()

            return obj.id


async def crud_reads(model, attr1: ColumnElement = None, attr2: any = None) -> list:
    async with async_session_maker() as session:
        async with session.begin():
            if not (attr1 is None or attr2 is None):
                stmt = select(model).where(attr1 == attr2)
                result = await session.execute(stmt)
            else:
                stmt = select(model)
                result = await session.execute(stmt)

            queries = result.all()
            objs = [query[0] for query in queries]

            return objs


async def crud_read(model, attr1: ColumnElement = None, attr2: any = None) -> any:
    async with async_session_maker() as session:
        async with session.begin():
            if not (attr1 is None or attr2 is None):
                stmt = select(model).where(attr1 == attr2)
                result = await session.execute(stmt)
            else:
                stmt = select(model)
                result = await session.execute(stmt)

            obj = result.first()

            return obj[0]


async def crud_update(model, schema: BaseModel, attr1: ColumnElement, attr2: any) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            stmt = update(model).where(attr1 == attr2).values(schema.model_dump())

            await session.execute(stmt)


async def crud_delete(model, attr1: ColumnElement, attr2: any) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            stmt = delete(model).where(attr1 == attr2)

            await session.execute(stmt)
