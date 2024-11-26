from typing import Optional

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_chroma import Chroma

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.utils import Output
from loguru import logger

from app.config.chat_model_config import system_template, chat_model
from app.model.dto.answer_model_dto import AnswerModelDTO
from app.model.dto.request_model_dto import RequestModelDTO

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def handle_chat_model_request(
        request: RequestModelDTO, vectorstore: Optional[Chroma]
) -> Optional[AnswerModelDTO]:

    try:
        chain_with_message_history: RunnableWithMessageHistory

        prompt_message = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_template,
                ),
                MessagesPlaceholder("chat_history"),
                (
                    "human",
                    "{input}",
                ),
            ]
        )

        if vectorstore:  # RAG-Version
            retriever = vectorstore.as_retriever()

            system_prompt_with_context = (
                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer "
                "the question. If you don't know the answer, say that you "
                "don't know and help otherwise. Keep the "
                "answer concise."
                "\n\n"
                "{context}"
            )

            prompt_message_with_context = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        system_prompt_with_context,
                    ),
                    MessagesPlaceholder("chat_history"),
                    (
                        "human",
                        "{input}",
                    ),
                ]
            )

            question_answer_chain = create_stuff_documents_chain(
                chat_model, prompt_message_with_context
            )

            history_aware_retriever = create_history_aware_retriever(
                chat_model, retriever, prompt_message
            )

            chain = create_retrieval_chain(
                history_aware_retriever, question_answer_chain
            )

            chain_with_message_history = RunnableWithMessageHistory(
                chain,
                get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )

            model_answer: Output = chain_with_message_history.invoke(
                {
                    "input": request.text,
                    "chat_history": get_session_history(request.session_id),
                },
                config={"configurable": {"session_id": request.session_id}},
            )

            return AnswerModelDTO(
                answer=model_answer["answer"],
            )

        else:  # Non-RAG-Version
            chain = prompt_message | chat_model

            chain_with_message_history = RunnableWithMessageHistory(
                chain,
                get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

            model_answer = chain_with_message_history.invoke(
                {
                    "input": request.text,
                    "chat_history": get_session_history(request.session_id),
                },
                config={"configurable": {"session_id": request.session_id}},
            )

            return AnswerModelDTO(
                answer=model_answer.content,
            )

    except Exception as e:
        logger.opt(exception=e).error(
            f"An error occurred while trying to do a reqeust to the chat model"
        )
        raise e
