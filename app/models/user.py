# app/models/user.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True # for orm_mode in Pydantic v1

class Token(BaseModel):
    access_token: str
    token_type: str