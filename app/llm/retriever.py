from typing import List
from langchain_core.documents import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from chroma import ChromaDBManager


class Retriever():
    def __init__(self, chroma: ChromaDBManager, k=20):
        self.chroma = chroma
        self.k = k

        # Initializer retriever
        base_retriever = chroma.as_retriever(search_kwargs={"k": k})

        # Add a reranker to rerank results
        self.retriever = ContextualCompressionRetriever(
            base_compressor=FlashrankRerank(top_n=k),
            base_retriever=base_retriever
        )

    def get_documents(self, query: str) -> List[Document]:
        return self.retriever.invoke(query)

    def get_documents_str(self, query: str) -> str:
        documents = self.get_documents(query)
        formatted_response = "\n".join(
            f"Document {i+1}:\n-----------\n{doc.page_content}\n" for i, doc in enumerate(documents)
        )
        return formatted_response

    # @staticmethod
    # def convert_to_doc(nutrition_data: List[str]) -> List[Document]:
    #     documents = []
    #     for food_item in nutrition_data:
    #         document = Document(page_content=food_item, metadata={
    #                             "source": 'memory'})  # Corrected to page_content
    #         documents.append(document)
    #     return documents
