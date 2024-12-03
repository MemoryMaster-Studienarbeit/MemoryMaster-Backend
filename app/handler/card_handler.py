import json
import uuid as uuid_module

from sqlalchemy.orm import Session as Db_session
from starlette.responses import JSONResponse

from app.model.dao.deck_model_dao import Deck, Session, Card
from app.model.dto.answer_model_dto import CardDTO


class CardHandler:

    async def create_card_handler(self, card_back: str, card_front: str, db: Db_session, deck_name: str, uuid: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(uuid=uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        deck = db.query(Deck).filter_by(deck_name=deck_name, uuid=uuid).first()
        if not deck:
            return JSONResponse(content="Deck was not found", status_code=404)

        new_card = Card(card_front=card_front, card_back=card_back, deck_id=deck.id, uuid=str(uuid_module.uuid4()))
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        card_dto = CardDTO(card_front=new_card.card_front, card_back=new_card.card_back, uuid=new_card.uuid)

        return JSONResponse(content=json.loads(card_dto.model_dump_json()), status_code=200)


    async def update_card_handler(self, card_back: str, card_front: str, card_uuid: str, db: Db_session, deck_name: str, session_uuid: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(uuid=session_uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        deck = db.query(Deck).filter_by(deck_name=deck_name, uuid=session_uuid).first()
        if not deck:
            return JSONResponse(content="Deck not found", status_code=404)

        card = db.query(Card).filter_by(uuid=card_uuid, deck_id=deck.id).first()
        if not card:
            return JSONResponse(content="Card not found", status_code=404)

        db.commit()
        db.refresh(card)
        card_dto = CardDTO(card_front=card_front, card_back=card_back, uuid=card.uuid)

        return JSONResponse(content=json.loads(card_dto.model_dump_json()), status_code=200)


    async def delete_card_handler(self, card_uuid: str, db: Db_session, deck_name: str, session_uuid: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(uuid=session_uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        deck = db.query(Deck).filter_by(deck_name=deck_name, uuid=session_uuid).first()
        if not deck:
            return JSONResponse(content="Deck not found", status_code=404)

        card = db.query(Card).filter_by(uuid=card_uuid, deck_id=deck.id).first()
        if not card:
            return JSONResponse(content="Card not found", status_code=404)

        db.delete(card)
        db.commit()

        return JSONResponse(content="Card deleted successfully", status_code=200)
