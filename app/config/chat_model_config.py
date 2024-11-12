import os

from langchain_groq import ChatGroq

chat_model = ChatGroq(
    temperature=0.3,
    model="llama3-8b-8192",
    api_key="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",
)

system_template = (
    "You are an expert tutor. "
    "Create exactly five flashcards based on the given topic. "
    "Each flashcard must strictly follow the format 'Question ; Answer ;;'. "
    "The output should only contain the flashcards in this format, without any additional text, explanations, or introductions. "
    "Respond with only the flashcards, nothing else. "
    "All content should be in English."
)
