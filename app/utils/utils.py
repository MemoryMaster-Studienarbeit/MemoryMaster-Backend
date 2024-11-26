import hashlib
import os
import re

from nltk import PorterStemmer

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