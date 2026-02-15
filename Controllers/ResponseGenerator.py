import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ResponseGenerator:

    def __init__(self):
        load_dotenv()

        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI( model="gemini-2.5-flash", google_api_key=self.GOOGLE_API_KEY,temperature=0.2)
        self.parser = StrOutputParser()

        self.nature_response_prompt = PromptTemplate(
            input_variables=["question", "sql", "data"],
            template="""
            user question: {question}
                sql qery used: {sql}
                data recevied: {data}
                YOUR TASK:
                Answer the user question in a nature language format based on data recevied.
                If the data is empty, say "No results found".
            """
        )

        self.nature_chain = self.nature_response_prompt | self.llm | self.parser

    def generate_natural_response(self, question: str, sql: str, data: str) -> str:
        return self.nature_chain.invoke({
            "question": question,
            "sql": sql,
            "data": data
        })

