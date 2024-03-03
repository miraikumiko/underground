from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)
from src.logger import logger
from src.payment.crud import crud_read_payments
from src.payment.schemas import PaymentCreate
from src.payment.payments import payment_request
from src.server.crud import crud_read_server
from src.user.models import User
from src.auth.utils import active_user

router = APIRouter(
    prefix="/api/payment",
    tags=["payments"]
)


@router.post("/checkout")
async def checkout(data: PaymentCreate, user: User = Depends(active_user)):
    try:
        server = await crud_read_server(data.server_id)

        if server is None:
            raise HTTPException(status_code=400, detail="Server doesn't exist")

        payments = await crud_read_payments(user.id)

        if payments:
            for payment in payments:
                if payment.active:
                    raise HTTPException(status_code=400, detail="You have active payment")

        data.user_id = user.id
        payment_uri = await payment_request(data, server.price)

        return {"payment_uri": payment_uri}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=None)
