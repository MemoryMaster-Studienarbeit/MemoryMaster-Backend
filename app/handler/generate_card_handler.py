import json
from typing import Optional

import chromadb
from loguru import logger
from sqlalchemy.orm import Session as Db_session
from starlette.responses import JSONResponse

from app.model.dao.deck_model_dao import Deck, Card
from app.model.dto.request_model_dto import RequestModelDTO, CustomFileModel
from app.services.chat_model_request_service import handle_chat_model_request
from app.services.file_handler_service import FileHandlerService
from app.utils.utils import generate_card_from_text

fileHandlerService = FileHandlerService()

file_store = {}

def get_file(session_uuid: str, deck_name: str) -> Optional[CustomFileModel]:
    unique_key = session_uuid + deck_name
    if unique_key not in file_store:
        file_store[unique_key] = None
    return file_store[unique_key]


def generate_card_handler(request: RequestModelDTO, db: Db_session, prompt_template: str, ai_model: str) -> JSONResponse:
    try:

        vectorstore = None
        all_documents = []

        if not get_file(request.uuid, request.deck.deck_name):
            file_store[request.uuid + request.deck.deck_name] = request.file

        client = chromadb.Client()
        collection = client.get_or_create_collection(name="collection")

        all_documents = fileHandlerService.csv_file_handler(
            all_documents, get_file(request.uuid, request.deck.deck_name)
        )

        if all_documents:
            # Split documents into manageable chunks for processing
            chunked_documents = fileHandlerService.chunk_handler(all_documents)

            # **Call knn_search()**
            query_indices = fileHandlerService.knn_search(chunked_documents, request.text)

            # Use the indices to retrieve the relevant documents
            relevant_documents = [chunked_documents[i] for i in query_indices]

            # Encode the relevant document chunks and store them in the database
            vectorstore = fileHandlerService.document_encoding_service(
                collection, relevant_documents
            )

        response = handle_chat_model_request(request, vectorstore, prompt_template, ai_model)

        try:
            card_dto = generate_card_from_text(response)
        except ValueError as e:
            logger.opt(exception=e).error(f"An error occurred while handling request")
            return JSONResponse(
                content={"answer": "An Internal Server Error occurred"}, status_code=500
            )

        deck_id = db.query(Deck).filter_by(uuid=request.uuid, deck_name=request.deck.deck_name).first().id

        card = Card(card_front=card_dto.card_front, card_back=card_dto.card_back, deck_id=deck_id, uuid=card_dto.uuid, last_learned=card_dto.last_learned, next_learned=card_dto.next_learned)
        db.add(card)
        db.commit()
        db.refresh(card)

        return JSONResponse(
            content=json.loads(card_dto.model_dump_json()), status_code=200
        )

    except Exception as e:
        logger.opt(exception=e).error(f"An error occurred while handling request")
        return JSONResponse(
            content={"answer": "An Internal Server Error occurred"}, status_code=500
        )
