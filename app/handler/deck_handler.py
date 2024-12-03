import json

from sqlalchemy.orm import Session as Db_session
from starlette.responses import JSONResponse

from app.model.dao.deck_model_dao import Deck, Session, Card
from app.model.dto.answer_model_dto import CardDTO, DeckDTO, SmallDeckDTO


class DeckHandler:

    async def get_deck_handler(self, db: Db_session, deck_name: str, uuid: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(uuid=uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        deck = db.query(Deck).filter_by(deck_name=deck_name, uuid=uuid).first()
        if not deck:
            return JSONResponse(content="Deck was not found", status_code=404)

        cards = db.query(Card).filter(Card.deck_id == deck.id).all()
        deck_dto = DeckDTO(
            deck_name=deck.deck_name,
            cards=[CardDTO(card_front=card.card_front, card_back=card.card_back, uuid=card.uuid) for card in cards]
        )

        return JSONResponse(content=json.loads(deck_dto.model_dump_json()), status_code=200)


    async def get_decks_handler(self, db: Db_session, uuid: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(uuid=uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        decks = db.query(Deck).filter(Deck.uuid == uuid).all()
        if not decks:
            return JSONResponse(content="No decks found for the given session_id", status_code=404)

        small_decks_dto = [SmallDeckDTO(deck_name=deck.deck_name) for deck in decks]

        return JSONResponse(content=json.loads(json.dumps([deck.model_dump() for deck in small_decks_dto])), status_code=200)


    async def create_deck_handler(self, db: Db_session, deck_name: str, uuid: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(uuid=uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        existing_deck = db.query(Deck).filter_by(deck_name=deck_name, uuid=uuid).first()
        if existing_deck:
            return JSONResponse(content="Deck already exists", status_code=400)

        new_deck = Deck(deck_name=deck_name, uuid=uuid)
        db.add(new_deck)
        db.commit()
        db.refresh(new_deck)
        deck_dto = DeckDTO(deck_name=new_deck.deck_name, cards=[])

        return JSONResponse(content=json.loads(deck_dto.model_dump_json()), status_code=200)


    async def delete_deck_handler(self, db: Db_session, deck_name: str, uuid: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(uuid=uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        deck = db.query(Deck).filter_by(deck_name=deck_name, uuid=uuid).first()
        if not deck:
            return JSONResponse(content="Deck was not found", status_code=404)

        db.delete(deck)
        db.commit()

        return JSONResponse(content="Deck deleted successfully", status_code=200)