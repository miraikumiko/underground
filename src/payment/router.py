from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)
from src.logger import logger
from src.payment.crud import crud_read_payment
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
async def checkout_server(data: PaymentCreate, user: User = Depends(active_user)):
    try:
        server = await crud_read_server({"id": data.server_id})

        if server is None:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "data": None,
                "details": "Server doesn't exist"
            })

        payment = await crud_read_payment({"user_id": user.id})

        if payment is not None:
            if payment.active == True:
                raise HTTPException(status_code=400, detail={
                    "status": "error",
                    "data": payment,
                    "details": "You have active payment"
                })

        payment_uri = await payment_request(data.server_id, server.price)

        data.user_id = user.id

        return {
            "status": "success",
            "data": payment_uri,
            "details": "Image has been uploaded"
        }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })
