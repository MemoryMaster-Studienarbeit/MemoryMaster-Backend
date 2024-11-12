from pydantic import BaseModel


class AnswerModelDTO(BaseModel):
    answer: str
