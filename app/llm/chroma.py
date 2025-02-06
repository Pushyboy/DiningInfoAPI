from typing import List
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os


class ChromaDBManager:
    """
    Manages the Chroma database, including initialization, adding documents,
    and creating a retriever.
    """

    def __init__(self, db_path: str = "chroma_db"):
        self.db_path = db_path
        self.embeddings = SentenceTransformerEmbeddings(
            modeL_name='all-MiniLM-L6-v2')
        self.vector_store = self.__initialize_chroma()

    def _initialize_chroma(self) -> Chroma:  # For testing purposes mostly
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            print(f"Loading existing Chroma from: {self.persist_directory}")
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        else:
            print(f"Creating new Chroma in: {self.persist_directory}")
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

    def add_documents(self, documents: List[Document]):
        if documents:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()

    def get_retriever(self, search_kwargs: dict = None):
        return self.vector_store.as_retriever(search_kwargs=search_kwargs or {})
