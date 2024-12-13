import asyncio
import secrets
import string
from sys import argv
from src.payment.schemas import PromoCreate
from src.payment.crud import crud_create_promo

count = int(argv[3])

for _ in range(count):
    code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    vds_id = int(argv[1])
    days = int(argv[2])

    promo_schema = PromoCreate(
        code=code,
        used=False,
        vds_id=vds_id,
        days=days
    )

    asyncio.run(crud_create_promo(promo_schema))
