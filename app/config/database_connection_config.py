from loguru import logger
from sqlalchemy import Engine
from sqlalchemy.orm import Session as Db_session

from app.model.dao.deck_model_dao import Base, Session, Deck

DATABASE = {
    "host": "localhost",
    "database": "MemoryMaster-Backend",
    "user": "memorymaster",
    "password": "memorymaster",
    "port": 5432,
}


def create_tables(engine: Engine) -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logger.info("Tables dropped and created successfully!")


def initialize_data(db: Db_session) -> None:
    new_session = Session(uuid="1")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    new_deck = Deck(deck_name="New Deck", uuid="1")
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)

    logger.info("Initial session and deck created successfully!")