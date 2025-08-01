from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    subscription_type: str  # "basic" or "premium"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

