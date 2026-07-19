from sqlmodel import SQLModel


class MessageResponse(SQLModel):
    success: bool
    message: str


class UploadedFileOut(SQLModel):
    path: str  # имя файла внутри UPLOADS_DIR
