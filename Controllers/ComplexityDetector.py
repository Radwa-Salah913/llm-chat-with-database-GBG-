import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from Models.get_schema import get_schema
from Models.get_description import get_description

class ComplexityDetector():
    def __init__(self):
       load_dotenv()
       self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
       self.llm = ChatGoogleGenerativeAI(model = "gemini-1.5-flash", google_api_key=self.GOOGLE_API_KEY, temperature=0.5)
       self.parser = StrOutputParser()
       self.schema = get_schema()
       self.description = get_description()
       self.detector_prompt = PromptTemplate(
           input_variables=["question","schema","description"],
           template="""
              You are an expert data analyst with extensive experience in working with complex databases and writing SQL queries.
              Your task is to evaluate the complexity of a user's question {question} based on the provided database schema {schema} and description {description}.
                - SIMPLE (can be answered with one SQL query)
                - COMPLEX (requires multiple reasoning steps)

              Return only one word.
            """
       )
       self.chain = self.detector_prompt | self.llm | self.parser

    def detect(self, question):
        return self.chain.invoke(question=question, schema=self.schema, description=self.description)