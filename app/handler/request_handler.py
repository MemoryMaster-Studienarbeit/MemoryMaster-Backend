import json
from urllib import response

from loguru import logger
from starlette.responses import JSONResponse

from app.model.dto.request_model_dto import RequestModelDTO
from app.services.chat_model_request_service import handle_chat_model_request


def request_handler(request: RequestModelDTO) -> JSONResponse:
    try:

        response = handle_chat_model_request(request)

        print(response)

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
