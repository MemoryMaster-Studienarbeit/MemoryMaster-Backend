from typing import Optional
from pydantic import BaseModel

from app.model.dto.answer_model_dto import DeckDTO


class CustomFileModel(BaseModel):
    file_type: str = ""
    file_content: str = ""

class RequestModelDTO(BaseModel):
    text: str
    uuid: str
    deck: DeckDTO
    file: Optional[CustomFileModel] = None

class GenerateCardDTO(BaseModel):
    text: str = ""
    appending_prompt_template: str = ""
    ai_model: str = ""
    file: Optional[CustomFileModel] = None

class CreateCardDTO(BaseModel):
    card_front: str = ""
    card_back: str = ""

class UpdateCardDTO(BaseModel):
    card_front: str = ""
    card_back: str = ""
    card_uuid: str = ""
