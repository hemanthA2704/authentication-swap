from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from schemas import mail_settings

router = APIRouter() 

conf = ConnectionConfig(
    MAIL_USERNAME=mail_settings.MAIL_USERNAME,
    MAIL_PASSWORD=mail_settings.MAIL_PASSWORD,
    MAIL_FROM=mail_settings.MAIL_FROM,
    MAIL_PORT=mail_settings.MAIL_PORT,
    MAIL_SERVER=mail_settings.MAIL_SERVER,
    MAIL_STARTTLS=mail_settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=mail_settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=mail_settings.USE_CREDENTIALS,
    VALIDATE_CERTS=mail_settings.VALIDATE_CERTS,
)
@router.post("/send-email/")
async def send_email(background_tasks: BackgroundTasks, email: EmailStr):
    message = MessageSchema(
        subject="FastAPI-Mail module",
        recipients=[email],  # List of recipients
        body="This is a test email from FastAPI",
        subtype="plain"
    )
    
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"message": "email has been sent"}
