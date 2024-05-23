from pydantic import BaseModel,EmailStr
from typing import Optional,List


class User(BaseModel):
    username : str 
    password : str


class CreateUser(User):
    confirm_password : str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class Details(BaseModel):
    name: str
    rgdno: int
    email: EmailStr
    org: str

class AdminValidation(BaseModel):
    user_id: str
    is_valid: bool
    remark : str | None = None
from pydantic_settings import BaseSettings

class MailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    class Config:
        env_file = ".env"

mail_settings = MailSettings()

class passwordChange(BaseModel):
    password : str


class composeMail(BaseModel):
    email : EmailStr
    subject : str
    remark : str
    