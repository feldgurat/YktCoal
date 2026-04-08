from sqlmodel import SQLModel


class MessageResponse(SQLModel):
    success: bool
    message: str
