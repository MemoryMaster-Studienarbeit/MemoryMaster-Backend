import datetime
import json
import uuid as uuid_module

from sqlalchemy.orm import Session as Db_session
from starlette.responses import JSONResponse

from app.model.dao.deck_model_dao import Deck, Session, Card
from app.model.dto.answer_model_dto import CardDTO
from app.model.dto.request_model_dto import UpdateCardDTO


class CardHandler:

    async def create_card_handler(self, card_back: str, card_front: str, db: Db_session, deck_name: str, session_uuid: str, last_learned: str, next_learned: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(session_uuid=session_uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        deck = db.query(Deck).filter_by(deck_name=deck_name, session_uuid=session_uuid).first()
        if not deck:
            return JSONResponse(content="Deck was not found", status_code=404)

        new_card = Card(card_front=card_front, card_back=card_back, deck_id= int(str(deck.id)), card_uuid=str(uuid_module.uuid4()), last_learned=last_learned, next_learned=next_learned)
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        card_dto = CardDTO(
            card_front=new_card.card_front,
            card_back=new_card.card_back,
            card_uuid=new_card.card_uuid,
            last_learned=new_card.last_learned,
            next_learned=new_card.next_learned,
            stage=new_card.stage
        )

        return JSONResponse(content=json.loads(card_dto.model_dump_json()), status_code=200)


    async def update_card_handler(self, session_uuid: str, deck_name: str, db: Db_session, update_card_dto: UpdateCardDTO ) -> JSONResponse:

        existing_session = db.query(Session).filter_by(session_uuid=session_uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        deck = db.query(Deck).filter_by(deck_name=deck_name, session_uuid=session_uuid).first()
        if not deck:
            return JSONResponse(content="Deck not found", status_code=404)

        card = db.query(Card).filter_by(card_uuid=update_card_dto.card_uuid, deck_id=deck.id).first()
        if not card:
            return JSONResponse(content="Card not found", status_code=404)

        card.card_front = update_card_dto.card_front
        card.card_back = update_card_dto.card_back
        card.last_learned = update_card_dto.last_learned
        card.next_learned = update_card_dto.next_learned
        card.stage = update_card_dto.stage

        db.commit()
        db.refresh(card)
        card_dto = CardDTO(
            card_front=update_card_dto.card_front,
            card_back=update_card_dto.card_back,
            card_uuid=card.card_uuid,
            last_learned=update_card_dto.last_learned,
            next_learned=update_card_dto.next_learned,
            stage=update_card_dto.stage
        )

        return JSONResponse(content=json.loads(card_dto.model_dump_json()), status_code=200)


    async def delete_card_handler(self, card_uuid: str, db: Db_session, deck_name: str, session_uuid: str) -> JSONResponse:

        existing_session = db.query(Session).filter_by(session_uuid=session_uuid).first()
        if not existing_session:
            return JSONResponse(content="Session not found", status_code=404)

        deck = db.query(Deck).filter_by(deck_name=deck_name, session_uuid=session_uuid).first()
        if not deck:
            return JSONResponse(content="Deck not found", status_code=404)

        card = db.query(Card).filter_by(card_uuid=card_uuid, deck_id=deck.id).first()
        if not card:
            return JSONResponse(content="Card not found", status_code=404)

        db.delete(card)
        db.commit()

        return JSONResponse(content="Card deleted successfully", status_code=200)
