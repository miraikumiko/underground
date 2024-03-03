from src.crud import (
    crud_create,
    crud_reads,
    crud_read,
    crud_update,
    crud_delete
)
from src.payment.models import Payment, Discount
from src.payment.schemas import (
    PaymentCreate,
    PaymentRead,
    PaymentUpdate,
    DiscountCreate,
    DiscountRead,
    DiscountUpdate
)


async def crud_create_payment(schema: PaymentCreate) -> int:
    payment_id = await crud_create(Payment, schema)

    return payment_id


async def crud_read_payments(user_id: int) -> list[PaymentRead]:
    payments = await crud_reads(Payment, attr1=Payment.user_id, attr2=user_id)

    return payments


async def crud_read_payment(payment_id: int) -> PaymentRead:
    payment = await crud_read(Payment, attr1=Payment.id, attr2=payment_id)

    return payment


async def crud_update_payment(schema: PaymentUpdate, payment_id: int) -> None:
    await crud_update(Payment, schema, attr1=Payment.id, attr2=payment_id)


async def crud_delete_payment(payment_id: int) -> None:
    await crud_delete(Payment, attr1=Payment.id, attr2=payment_id)


async def crud_create_discount(schema: DiscountCreate) -> int:
    discount_id = await crud_create(Discount, schema)

    return discount_id


async def crud_read_discounts() -> list[DiscountRead]:
    discounts = await crud_reads(Discount)

    return discounts


async def crud_read_discount(user_id: int) -> DiscountRead:
    discount = await crud_read(Discount, attr1=Discount.user_id, attr2=user_id)

    return discount


async def crud_update_discount(schema: DiscountUpdate, user_id: int) -> None:
    await crud_update(Discount, schema, attr1=Discount.user_id, attr2=user_id)


async def crud_delete_discount(user_id: int) -> None:
    await crud_delete(Discount, attr1=Discount.user_id, attr2=user_id)
