from pydantic import BaseModel


class DeleteResponse(BaseModel):
    success: bool
    status: str