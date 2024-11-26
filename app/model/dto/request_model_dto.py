from typing import Optional
from pydantic import BaseModel


class CustomFileModel(BaseModel):
    file_type: str
    file_content: str


class RequestModelDTO(BaseModel):
    text: str
    session_id: str
    file: Optional[CustomFileModel] = None