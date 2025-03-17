import hashlib
import os
import re
import uuid as uuid_module

from nltk import PorterStemmer

from app.model.dto.answer_model_dto import CardDTO

stemmer = PorterStemmer()

def clean_text(text: str) -> str:

    text = re.sub(r"\W", " ", text)
    text = text.lower()
    text = " ".join(stemmer.stem(word) for word in text.split())

    return text


def generate_csv_filename_from_name(name: str) -> str:

    hash_object = hashlib.md5(name.encode())
    hex_dig = hash_object.hexdigest()
    directory = "app/data"

    if not os.path.exists(directory):
        os.makedirs(directory)

    return f"{directory}/{hex_dig}.csv"


def generate_card_from_text(text: str) -> CardDTO:

    try:
        question, answer = text.split(';', 1)
    except ValueError:
        raise ValueError("Input text must contain exactly one ';' character separating the question and answer.")

    return CardDTO(card_front=question.strip(), card_back=answer.strip(), card_uuid=str(uuid_module.uuid4()), last_learned="", next_learned="", stage=0)