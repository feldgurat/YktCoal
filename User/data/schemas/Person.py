

from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    contactNumber: str = Field(min_length=1, max_length=30)
    telegramUserId: Optional[str] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    contactNumber: Optional[str] = Field(default=None, min_length=1, max_length=30)
    telegramUserId: Optional[str] = None


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    contactNumber: str
    telegramUserId: Optional[str] = None
    isAdmin: bool