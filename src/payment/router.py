from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)
from src.logger import logger
from src.payment.payments import payment_request
from src.payment.schemas import PaymentCreate
from src.server.crud import crud_get_server
from src.user.models import User
from src.auth.utils import active_user

router = APIRouter(
    prefix="/api/payment",
    tags=["payments"]
)


@router.post("/checkout")
async def checkout_server(data: PaymentCreate, user: User = Depends(active_user)):
    try:
        server = await crud_get_server(data.server_id)

        if server is None:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "data": None,
                "details": "Server doesn't exist"
            })

        payment_uri = await payment_request(data.server_id, server.price)

        data.user_id = user.id

        return payment_uri
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": "Server error"
        })
