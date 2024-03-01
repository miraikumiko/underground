from pydantic import BaseModel
from sqlalchemy import select, update, delete
from src.database import async_session_maker
from src.models import Base
from src.utils import err_catch


@err_catch
async def crud_create(Model: Base, Schema: BaseModel) -> int:
    async with async_session_maker() as session:
        async with session.begin():
            obj = Model(Schema.model_dump())

            session.add(obj)
            await session.commit()

            return obj.id


@err_catch
async def crud_read(
        Model: Base,
        Schema: BaseModel = None,
        attr1: any = None,
        attr2: any = None,
        all: bool = False
) -> BaseModel | list[BaseModel]:
    async with async_session_maker() as session:
        async with session.begin():
            if all:
                if Schema is None:
                    stmt = select(Model)
                    result = await session.execute(stmt)
                    queries = result.all()
                    objs = [query[0] for query in queries]
                else:
                    if not (attr1 is None or attr2 is None):
                        stmt = select(Model).where(attr1 == attr2)
                        result = await session.execute(stmt)
                        queries = result.all()
                        objs = [query[0] for query in queries]
                    else:
                        stmt = select(Model).where(Model.id == Schema.id)
                        result = await session.execute(stmt)
                        queries = result.all()
                        objs = [query[0] for query in queries]

                return objs
            else:
                if not (attr1 is None or attr2 is None):
                    stmt = select(Model).where(attr1 == attr2)
                    result = await session.execute(stmt)
                    queries = result.all()
                    objs = [query[0] for query in queries]
                else:
                    stmt = select(Model).where(Model.id == Schema.id)
                    result = await session.execute(stmt)
                    obj = result.first()[0]

                return obj


@err_catch
async def crud_update(Model: Base, Schema: BaseModel) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            stmt = update(Model).where(Model.id == Schema.id).values(Schema.model_dump())

            await session.execute(stmt)


@err_catch
async def crud_delete(Model: Base, Schema: BaseModel) -> None:
     async with async_session_maker() as session:
        async with session.begin():
            stmt = delete(Model).where(Model.id == Schema.id)

            await session.execute(stmt)
