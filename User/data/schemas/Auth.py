from pydantic import BaseModel, Field


class SmsRequestIn(BaseModel):
    phone: str = Field(examples=["+79991234567"])


class SmsVerifyIn(BaseModel):
    phone: str = Field(examples=["+79991234567"])
    code: str = Field(min_length=4, max_length=8, examples=["123456"])

class SmsCodeRequestAnswer(BaseModel):
    status: str = Field(examples=["ok"])
    message: str = Field(examples=["Код отправлен"])

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshIn(BaseModel):
    refresh_token: str

class RegisterAnswer(BaseModel):
    success: bool
    status: str