import base64
import io
import os
import uuid
from typing import Optional, Union

from chromadb.api.models.Collection import Collection
from langchain_chroma.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd
from PyPDF2 import PdfReader
from loguru import logger
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from langchain_text_splitters import RecursiveCharacterTextSplitter
import concurrent.futures

from app.model.dto.request_model_dto import CustomFileModel
from app.utils.utils import generate_csv_filename_from_name, clean_text

DOCUMENTS_LIMIT = 45
QUERY_RESULTS_LIMIT = 10
CHUNK_SIZE = 600
CHUNK_OVERLAP = 50
BATCH_SIZE = 10
TRANSFORMER_DIMENSIONS = 768
MAX_URL_DEPTH = 5

class DatabaseService:
    def __init__(self):
        self.model_transformer = SentenceTransformer(
            "mixedbread-ai/mxbai-embed-large-v1",
            truncate_dim=TRANSFORMER_DIMENSIONS,
            device="cpu",
        )
        self.vectorizer = TfidfVectorizer()

    def csv_file_handler(
            self, all_documents: list, file: Optional[CustomFileModel]
    ) -> list[str]:
        try:

            # TODO: add docx file type
            if file:
                if file.file_type == "text/plain":
                    decoded_content = base64.b64decode(file.file_content).decode("utf-8")
                elif file.file_type == "application/pdf":
                    decoded_content = base64.b64decode(file.file_content)
                    pdf_reader = PdfReader(io.BytesIO(decoded_content))
                    decoded_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
                else:
                    logger.warning(f"The provided file could not be handled.")
                    return all_documents

                # Generate a unique filename for the CSV
                csv_file = generate_csv_filename_from_name(decoded_content)

                if os.path.exists(csv_file):
                    # If the CSV file already exists, read it
                    df = pd.read_csv(csv_file)
                else:
                    # If the CSV file does not exist, generate it
                    df = self.generate_csv_from_file(csv_file, decoded_content)

                all_documents.extend(df["text"].tolist())

            return all_documents
        except Exception as e:
            logger.opt(exception=e).error(
                f"An error occurred while handling the CSV file"
            )

    def generate_csv_from_file(self, csv_file: str, file_content: str) -> pd.DataFrame:
        try:
            # Clean the text content
            cleaned_content = clean_text(file_content)

            # Split the cleaned content into documents (for simplicity, we assume each line is a document)
            documents = [{"text": line} for line in cleaned_content.split("\n") if line]

            # Add the documents to a DataFrame and save it as a CSV file
            df = pd.DataFrame(documents)
            df.drop_duplicates(subset=["text"], inplace=True)
            df.to_csv(csv_file, index=False)
            return df
        except Exception as e:
            logger.opt(exception=e).info(
                f"An error occurred while generating the CSV file from the file content"
            )
            return pd.DataFrame()

    def chunk_handler(self, all_documents: list):
        try:
            # Limit the number of documents to process
            all_documents = all_documents[:DOCUMENTS_LIMIT]
            chunked_documents = []

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len,
                is_separator_regex=True,
            )

            for doc in all_documents:
                # Split each document into chunks
                chunked_documents.extend(text_splitter.split_text(doc))

            return chunked_documents
        except Exception as e:
            logger.opt(exception=e).error(f"An error occurred while handling chunks")

    def knn_search(self, documents: list[str], query: str, k: int = 5):
        try:

            tfidf_matrix = self.vectorizer.fit_transform(documents)

            num_documents = tfidf_matrix.shape[0]
            k = min(k, num_documents)
            knn = NearestNeighbors(n_neighbors=k, metric="cosine")
            knn.fit(tfidf_matrix)

            query_tfidf = self.vectorizer.transform([clean_text(query)])
            distances, indices = knn.kneighbors(query_tfidf)

            return indices.flatten()
        except Exception as e:
            logger.opt(exception=e).error(f"An error occurred while performing KNN search")


    def document_encoding_service(
            self, collection: Collection, relevant_documents: list[Union[str, list[str]]]
    ) -> Optional[Chroma]:
        try:
            # Generate unique IDs for each document chunk
            ids = [str(uuid.uuid4()) for _ in range(len(relevant_documents))]

            # Split chunked_documents into batches
            def encode_documents_batch(documents_batch):
                return self.model_transformer.encode(documents_batch).tolist()

            document_batches = [
                relevant_documents[i : i + BATCH_SIZE]
                for i in range(0, len(relevant_documents), BATCH_SIZE)
            ]

            # Use ThreadPoolExecutor to encode document batches concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(encode_documents_batch, batch)
                    for batch in document_batches
                ]
                document_embeddings = [
                    embedding
                    for future in concurrent.futures.as_completed(futures)
                    for embedding in future.result()
                ]
            executor.shutdown(wait=True)

            # Store the document chunks and their embeddings in the database
            collection.upsert(
                documents=relevant_documents,
                embeddings=document_embeddings,
                ids=ids,
            )

            vector_db = Chroma(
                collection_name="collection",
                embedding_function=HuggingFaceEmbeddings(),
            )

            return vector_db
        except Exception as e:
            logger.opt(exception=e).error(f"An error occurred while encoding documents")