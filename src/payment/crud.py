from sqlalchemy import select, update
from sqlalchemy.engine.row import Row
from src.database import async_session_maker
from src.payment.models import Discount, Payment
from src.server.models import Server
from src.payment.schemas import (
    PaymentCreate,
    PaymentUpdate
)


async def crud_add_discount(server_id: int, user_id: int) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(Server).where(Server.id == server_id)
                result = await session.execute(stmt)
                server = result.first()[0]

                stmt = select(Discount).where(Discount.user_id == user_id)
                result = await session.execute(stmt)
                discount = result.first()

                if discount is None:
                    discount = Discount()
                    discount.user_id = user_id
                    discount.discount = server.price / 5

                    session.add(discount)
                else:
                    stmt = update(Discount).where(
                        Discount.user_id == user_id
                    ).values(discount=(discount[0] + server.price / 5))
                    await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_add_payment(data: PaymentCreate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                payment = Payment()
                payment.user_id = data.user_id
                payment.server_id = data.server_id
                payment.active_server_id = data.active_server_id
                payment.payment_id = data.payment_id
                payment.amount = data.amount
                payment.month = data.month
                payment.active = data.active

                session.add(payment)
            except Exception as e:
                raise e


async def crud_get_payment(payment_id: str) -> Row | Exception:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(Payment).where(Payment.payment_id == payment_id)
                result = await session.execute(stmt)
                payment = result.first()[0]

                return payment
            except Exception as e:
                raise e


async def crud_update_payment(payment_id: str, data: PaymentUpdate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = update(Payment).where(
                    Payment.payment_id == payment_id
                ).values(data)
                await session.execute(stmt)
            except Exception as e:
                raise e
