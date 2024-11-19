import json
import sys

from fastapi import FastAPI, HTTPException
from loguru import logger
from requests import session
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.websockets import WebSocketDisconnect, WebSocket

from app.handler.request_handler import request_handler
from app.model.dto.request_model_dto import RequestModelDTO

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

@app.post("/receiveQuestion")
async def receive_question(data: str):
    try:

        request_dto = RequestModelDTO(text=data, session_id="1")

        response = request_handler(request_dto)

        return {"answer": response.body.decode()}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.websocket("/ws/receiveQuestion")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            request = RequestModelDTO(**json.loads(data))

            response = request_handler(request)

            await websocket.send_text(response.body.decode())
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await websocket.send_text(json.dumps({"message": "Internal Server Error"}))
        await websocket.close()
