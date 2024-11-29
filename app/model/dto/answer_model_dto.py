from typing import Optional

from pydantic import BaseModel


class CardDTO(BaseModel):
    uuid: str
    card_front: str
    card_back: str


class DeckDTO(BaseModel):
    deck_name: str
    cards: Optional[list[CardDTO]] = None


class SmallDeckDTO(BaseModel):
    deck_name: str

