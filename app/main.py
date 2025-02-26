import sys
from typing import Generator

from fastapi import FastAPI, HTTPException, Depends
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as Db_session
from starlette.responses import JSONResponse

from app.config.chat_model_config import system_template
from app.config.database_connection_config import create_tables, initialize_data
from app.handler.deck_handler import DeckHandler
from app.handler.generate_card_handler import generate_card_handler
from app.handler.session_handler import SessionHandler
from app.model.dao.deck_model_dao import  Session
from app.model.dto.answer_model_dto import DeckDTO
from app.model.dto.request_model_dto import RequestModelDTO, GenerateCardDTO, CreateCardDTO, UpdateCardDTO
from app.handler.card_handler import CardHandler

origins = [
    "http://localhost",
    "http://localhost:3000",
]

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)

app = FastAPI(
    title="Memory-Master-Backend",
    description="This is the backend to the Memory-Master",
    version="0.1.0",
    root_path="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://memorymaster:memorymaster@postgres:5432/MemoryMaster-Backend"
engine = create_engine(DATABASE_URL)

def get_db() -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event() -> None:
    create_tables(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    initialize_data(db)


@app.get(
    "/health",
    name="Health Check",
    description="Check the health of the backend",
    responses={
        200: {"description": "Backend is healthy", "content": {"application/json": {}}}
    },
)
async def health_endpoint() -> str:
    return "Backend is healthy"


@app.post(
    "/uuid",
    name="Create UUID",
    description="Creates a new UUID if it's not already existing",
    responses={
        200: {"description": "UUID created/found successfully", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def get_or_create_session_uuid(
        uuid: str,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        return await SessionHandler().get_or_create_session_handler(db, uuid)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get(
    "/deck",
    name="Get Deck",
    description="Get a deck",
    responses={
        200: {"description": "Deck found successfully", "content": {"application/json": {}}},
        404: {"description": "Deck/Session not found", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def get_deck(
        uuid: str,
        deck_name: str,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        return await DeckHandler().get_deck_handler(db, deck_name, uuid)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get(
    "/decks",
    name="Get Decks",
    description="Get all decks from a session",
    responses={
        200: {"description": "Decks found successfully", "content": {"application/json": {}}},
        404: {"description": "Deck/Session not found", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def get_decks(
        uuid: str,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        return await DeckHandler().get_decks_handler(db, uuid)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post(
    "/deck",
    name="Create Deck",
    description="Create a deck",
    responses={
        200: {"description": "Deck created successfully", "content": {"application/json": {}}},
        400: {"description": "Deck already exists", "content": {"application/json": {}}},
        404: {"description": "Session not found", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def create_deck(
        uuid: str,
        deck_name: str,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        return await DeckHandler().create_deck_handler(db, deck_name, uuid)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete(
    "/deck",
    name="Delete Deck",
    description="Delete a deck",
    responses={
        200: {"description": "Deck deleted successfully", "content": {"application/json": {}}},
        404: {"description": "Deck not found", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def delete_deck(
        uuid: str,
        deck_name: str,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        return await DeckHandler().delete_deck_handler(db, deck_name, uuid)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post(
    "/generateCard",
    name="Generate Card",
    description="Generate a card from the LLM model",
    responses={
        200: {"description": "Card generated successfully", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def generate_card(
        uuid: str,
        deck_name: str,
        generate_card_dto: GenerateCardDTO,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        deck_dto = DeckDTO(deck_name=deck_name, cards=[])
        request_dto = RequestModelDTO(text=generate_card_dto.text, uuid=uuid, deck=deck_dto, file=generate_card_dto.file)

        full_prompt_template = system_template + "\n" + generate_card_dto.appending_prompt_template

        if generate_card_dto.ai_model == "":
            ai_model = "llama3-8b-8192"
        else:
            ai_model = generate_card_dto.ai_model

        return generate_card_handler(request_dto, db, full_prompt_template, ai_model)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post(
    "/createCard",
    name="Create Card",
    description="Create a card for a given deck",
    responses={
        200: {"description": "Card created successfully", "content": {"application/json": {}}},
        404: {"description": "Session or Deck not found", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def create_card(
        uuid: str,
        deck_name: str,
        create_card_dto: CreateCardDTO,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        return await CardHandler().create_card_handler(create_card_dto.card_back, create_card_dto.card_front, db, deck_name, uuid)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put(
    "/card",
    name="Update Card",
    description="Update a card for a given deck",
    responses={
        200: {"description": "Card updated successfully", "content": {"application/json": {}}},
        404: {"description": "Card not found", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def update_card(
        session_uuid: str,
        deck_name: str,
        update_card_dto: UpdateCardDTO,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        return await CardHandler().update_card_handler(update_card_dto.card_back, update_card_dto.card_front, update_card_dto.card_uuid, db, deck_name, session_uuid)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete(
    "/card",
    name="Delete Card",
    description="Delete a card from a given deck",
    responses={
        200: {"description": "Card deleted successfully", "content": {"application/json": {}}},
        404: {"description": "Card not found", "content": {"application/json": {}}},
        500: {"description": "Internal Server Error", "content": {"application/json": {}}},
    }
)
async def delete_card(
        session_uuid: str,
        deck_name: str,
        card_uuid: str,
        db: Db_session = Depends(get_db)
) -> JSONResponse:
    try:
        return await CardHandler().delete_card_handler(card_uuid, db, deck_name, session_uuid)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")