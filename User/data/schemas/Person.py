

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    birthDate: Optional[date] = None
    contactNumber: str = Field(min_length=1, max_length=30)

    email: EmailStr
    telegramUserName: Optional[str] = Field(default=None, max_length=255)
    telegramUserId: Optional[str] = None


    password: str = Field(min_length=6, max_length=255)


    isAdmin: bool = False


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    birthDate: Optional[date] = None
    contactNumber: Optional[str] = Field(default=None, min_length=1, max_length=30)

    email: Optional[EmailStr] = None
    telegramUserName: Optional[str] = Field(default=None, max_length=255)
    telegramUserId: Optional[str] = None

    isAdmin: Optional[bool] = None


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    birthDate: Optional[date] = None
    contactNumber: str

    email: EmailStr
    telegramUserName: Optional[str] = None
    telegramUserId: Optional[str] = None

    isAdmin: bool
