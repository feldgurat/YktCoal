from sqlmodel import SQLModel, Field


class SmsRequestIn(SQLModel):
    phone: str = Field(min_length=10, max_length=20)


class SmsVerifyIn(SQLModel):
    phone: str = Field(min_length=10, max_length=20)
    code: str = Field(min_length=4, max_length=6)


class RefreshIn(SQLModel):
    refresh_token: str


class TokenPair(SQLModel):
    access_token: str
    refresh_token: str


class RegisterIn(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    contact_number: str = Field(min_length=10, max_length=20)
    telegram_user_id: str | None = None
    address: str | None = None


class RegisterOut(SQLModel):
    success: bool
    message: str

class LogoutIn(SQLModel):
    refresh_token: str