from smtplib import SMTP_SSL
from src.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_SENDER
)


async def sendmail(subject: str, body: str, email: str) -> None | Exception:
    with SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        message = f"Subject: {subject}\n{body}"

        try:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER, email, message)
        except Exception as e:
            raise e
