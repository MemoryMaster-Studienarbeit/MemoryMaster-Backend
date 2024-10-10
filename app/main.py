import sys

from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

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

