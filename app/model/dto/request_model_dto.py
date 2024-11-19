from pydantic import BaseModel

class RequestModelDTO(BaseModel):
    text: str
    session_id: str