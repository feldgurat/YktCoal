from sqlmodel import SQLModel


class TgRegisterIn(SQLModel):
    telegram_user_id: str
    phone: str
    name: str
    address: str | None = None


class TgLinkIn(SQLModel):
    telegram_user_id: str
    phone: str
