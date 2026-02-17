import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from Models.get_schema import get_schema
from Models.get_description import get_description
from pydantic import BaseModel, Field
from typing import List
import json

# output format:
class SubQuestion(BaseModel):
    sub_question: List[str] = Field( ..., description="A list of sub-questions derived from the original question.")


class Decomposition():
    def __init__(self):
       load_dotenv()
       GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
       llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.0)

       self.llm = llm.with_structured_output(SubQuestion)
       self.schema = get_schema()
       self.description = get_description()
       self.json_schema = json.dumps(SubQuestion.model_json_schema(), ensure_ascii=False)

       self.decompose_prompt = PromptTemplate(
           input_variables=["question","schema","description"],
           template="""
            You are a database query decomposition engine.

            Your task is to break the given complex user question into smaller sub-questions.

            Rules:
            - Each sub-question must be answerable using ONE SQL query only.
            - Do NOT generate SQL.
            - Do NOT explain anything.
            - Do NOT repeat the original question.
            - Sub-questions must be logically ordered.
            - Avoid redundant steps.
            - Use only entities (tables/columns) that exist in the provided schema.
            - Each sub-question must represent a concrete data retrieval step.
            - If required information does not exist in the schema, do NOT invent it.
            - Return ONLY structured JSON.
            - Do NOT include any text outside the JSON.

            -------------------------
            DATABASE SCHEMA:
            <SCHEMA>
            {schema}
            </SCHEMA>

            -------------------------
            TABLE DESCRIPTIONS:
            <DESCRIPTION>
            {description}
            </DESCRIPTION>

            -------------------------
            USER QUESTION:
            {question}

            -------------------------
            OUTPUT JSON SCHEMA:
            {json_schema}


            """
       )
       self.chain = self.decompose_prompt | self.llm | self.parser


    def decompose(self, question):
        return self.chain.invoke({"question": question, "schema": self.schema, "description": self.description})