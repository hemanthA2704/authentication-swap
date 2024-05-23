from database import Base
from sqlalchemy import Column, Integer, String, Boolean, text
from pydantic import EmailStr

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True ,index=True)
    username = Column(String,nullable=False)
    password = Column(String,nullable=False)

class Registration(Base):
    __tablename__ = "requests"
    id = Column(Integer,primary_key=True ,index=True)
    user_id=Column(String,nullable=False)
    name = Column(String,nullable=False)
    rgdno = Column(Integer,nullable=False)
    email = Column(String,nullable=False)
    org = Column(String,nullable=False)
    approved = Column(Boolean,nullable=False)
