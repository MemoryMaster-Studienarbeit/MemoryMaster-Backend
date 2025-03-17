from typing import Optional

from pydantic import BaseModel


class CardDTO(BaseModel):
    card_uuid: str
    card_front: str
    card_back: str
    last_learned: str = ""
    next_learned: str = ""
    stage: int = 0

class DeckDTO(BaseModel):
    deck_name: str
    cards: Optional[list[CardDTO]] = None


class SmallDeckDTO(BaseModel):
    deck_name: str

