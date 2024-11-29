from typing import Optional
from pydantic import BaseModel

from app.model.dto.answer_model_dto import DeckDTO


class CustomFileModel(BaseModel):
    file_type: str
    file_content: str


class RequestModelDTO(BaseModel):
    text: str
    uuid: str
    deck: DeckDTO
    file: Optional[CustomFileModel] = None