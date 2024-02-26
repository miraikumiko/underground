from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from src.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_SENDER
)

email_config = ConnectionConfig(
    MAIL_USERNAME = SMTP_USER,
    MAIL_PASSWORD = SMTP_PASSWORD,
    MAIL_FROM = SMTP_SENDER,
    MAIL_PORT = SMTP_PORT,
    MAIL_SERVER = SMTP_HOST,
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


async def sendmail(subject: str, body: str, email: str) -> None | Exception:
    message = MessageSchema(
        subject=subject,
        recipients={email},
        body=body,
        subtype=MessageType.plain
    )

    try:
        fm = FastMail(email_config)
        await fm.send_message(message)
    except Exception as e:
        raise e
