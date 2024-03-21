from email.message import EmailMessage
from email.utils import formatdate
from aiosmtplib import send
from src.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_SENDER
)
from src.logger import logger


async def sendmail(subject: str, body: str, email: str) -> None:
    try:
        message = EmailMessage()
        message["From"] = SMTP_SENDER
        message["To"] = email
        message["Subject"] = subject
        message["Date"] = formatdate()
        message.set_content(body)

        await send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=True
        )
    except Exception as e:
        logger.info(e)
        raise e
