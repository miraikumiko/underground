from src.crud import (
    crud_create,
    crud_read,
    crud_update,
    crud_delete
)
from src.payment.models import Payment, Discount
from src.payment.schemas import (
    PaymentCreate,
    PaymentRead,
    PaymentUpdate,
    PaymentDelete,
    DiscountCreate,
    DiscountRead,
    DiscountUpdate,
    DiscountDelete
)


async def crud_create_payment(Schema: PaymentCreate) -> int:
    id = await crud_create(Payment, Schema)

    return id


async def crud_read_payments() -> list[PaymentRead]:
    payments = crud_read(Payment, all=True)

    return payments


async def crud_read_payment(Schema: PaymentRead) -> PaymentRead:
    if Schema.id is None:
        server = await crud_read(
            Payment,
            Schema,
            attr1=Payment.user_id,
            attr2=Schema.user_id
        )
    else:
        server = await crud_read(Payment, Schema)

    return server


async def crud_update_payment(Schema: PaymentUpdate) -> None:
    await crud_update(Payment, Schema)


async def crud_delete_payment(Schema: PaymentDelete) -> None:
    await crud_delete(Payment, Schema)


async def crud_create_discount(Schema: DiscountCreate) -> int:
    id = await crud_create(Discount, Schema)

    return id


async def crud_read_discounts() -> list[DiscountRead]:
    discounts = crud_read(Discount, all=True)

    return discounts


async def crud_read_discount(Schema: DiscountRead) -> DiscountRead:
    if Schema.id is None:
        discount = await crud_read(
            Discount,
            Schema,
            attr1=Discount.user_id,
            attr2=Schema.user_id
        )
    else:
        discount = await crud_read(Discount, Schema)

    return discount


async def crud_update_discount(Schema: DiscountUpdate) -> None:
    await crud_update(Discount, Schema)


async def crud_delete_discount(Schema: DiscountDelete) -> None:
    await crud_delete(Discount, Schema)
