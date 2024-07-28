from pydantic import BaseModel, EmailStr
from typing import Union, Optional
from datetime import datetime


class BaseUserSchemas(BaseModel):
    id: Optional[int]
    username: str
    password: Optional[str]
    email: Optional[EmailStr]


class FullUserSchemas(BaseUserSchemas):
    first_name: str
    last_name: str
    date_of_created: Optional[datetime]
    date_of_update: Optional[datetime]
    refresh_token: Optional[str]
    role: Optional[str]
    

class UserRSchemas(BaseUserSchemas):
    refresh_token: Optional[str]