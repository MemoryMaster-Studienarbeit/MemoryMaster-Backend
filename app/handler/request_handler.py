import json
from typing import Optional

import chromadb
from loguru import logger
from starlette.responses import JSONResponse

from app.model.dto.request_model_dto import RequestModelDTO, CustomFileModel
from app.services import database_service
from app.services.chat_model_request_service import handle_chat_model_request
from app.services.database_service import DatabaseService

database_service = DatabaseService()
file_store = {}

def get_file(session_id: str) -> Optional[CustomFileModel]:
    if session_id not in file_store:
        file_store[session_id] = None
    return file_store[session_id]

def request_handler(request: RequestModelDTO) -> JSONResponse:
    try:

        vectorstore = None
        all_documents = []

        if not get_file(request.session_id):
            file_store[request.session_id] = request.file

        client = chromadb.Client()
        collection = client.get_or_create_collection(name="collection")

        all_documents = database_service.csv_file_handler(
            all_documents, get_file(request.session_id)
        )

        if all_documents:
            # Split documents into manageable chunks for processing
            chunked_documents = database_service.chunk_handler(all_documents)

            # **Call knn_search()**
            query_indices = database_service.knn_search(chunked_documents, request.text)

            # Use the indices to retrieve the relevant documents
            relevant_documents = [chunked_documents[i] for i in query_indices]

            # Encode the relevant document chunks and store them in the database
            vectorstore = database_service.document_encoding_service(
                collection, relevant_documents
            )

        response = handle_chat_model_request(request, vectorstore)

        if response is None:
            return JSONResponse(
                content={"answer": "No relevant information was found"}, status_code=404
            )

        return JSONResponse(
            content=json.loads(response.model_dump_json()), status_code=200
        )

    except Exception as e:
        logger.opt(exception=e).error(f"An error occurred while handling request")
        return JSONResponse(
            content={"answer": "An Internal Server Error occurred"}, status_code=500
        )
