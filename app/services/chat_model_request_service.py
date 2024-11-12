from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.utils import Output
from loguru import logger

from app.config.chat_model_config import chat_model, system_template
from app.model.dto.answer_model_dto import AnswerModelDTO
from app.model.dto.request_model_dto import RequestModelDTO


def handle_chat_model_request(
        request: RequestModelDTO
) -> AnswerModelDTO | None:

    try:

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{text}")]
        )

        chain = prompt_template | chat_model
        model_answer: Output = chain.invoke({"language": "english", "text": request.text})

        return AnswerModelDTO(
            answer=model_answer.content,
        )

    except Exception as e:
        logger.opt(exception=e).error(
            f"An error occurred while trying to do a reqeust to the chat model"
        )
        raise e