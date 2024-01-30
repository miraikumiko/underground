from src.user.crud import crud_add_discount


async def payment_checkout_with_xmr(server_id: int, user_id: int):
    await crud_add_discount(server_id, user_id)


async def payment_checkout_with_paypal(server_id: int, user_id: int):
    await crud_add_discount(server_id, user_id)
