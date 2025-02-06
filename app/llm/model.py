from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.llm.chroma import ChromaDBManager
from app.llm.retriever import Retriever


class Model:
    def __init__(self, chroma: ChromaDBManager):
        self.retriever = Retriever(chroma=chroma)
        self.init_model()

    def init_model(self):
        template = """
        You are a nutrition chatbot for the University of Rochester Dining Hall. 
        Your goal is to provide the best nutritional advice and food recommendations to students, 
        strictly based on the list of available foods at the dining hall.

        **Instructions:**
        1.  **Nutritional Focus:** Prioritize nutritional value for bodybuilding and general health when giving advice.
        2.  **Dining Hall Foods ONLY:**  Your recommendations MUST come from the 'Available Foods' list below. Do not recommend foods outside of this list.
        3.  **Be Concise and Actionable:** Provide clear, direct advice and food suggestions.
        4.  **Professional Style:** Maintain a professional yet approachable tone, appropriate for a University setting.

        **Conversation History:**
        {history}

        **Available Foods:**
        {context}

        **Student's Question:** {question}

        Response:"""

        prompt = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI(model='gpt-4o-mini')

        self.chain = (
            {
                "context": self.retriever.get_documents_str,
                "history": RunnablePassthrough(),
                "question": RunnablePassthrough()
            }
            | prompt
            | model
            | StrOutputParser()
        )

    def query(self, query: str, history: str = ""):
        results = self.chain.invoke({"question": query, "history": history})
        return results
