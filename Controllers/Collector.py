import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class Collector():
    def __init__(self):
       load_dotenv()
       GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

       self.llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.5)
       self.parser = StrOutputParser()
      
       self.collector_prompt = PromptTemplate(
           input_variables=["question", "results"],
           template="""
                You are a data reasoning engine.

                You are given:
                1) The original complex question.
                2) The execution results of multiple sub-questions that were generated to solve it.

                Original Question:
                {question}

                Sub-question Results (Structured Data):
                {results}

                Instructions:
                - Use ONLY the provided results.
                - Do NOT assume any missing information.
                - Do NOT generate explanations.
                - If numerical calculation is required, compute it precisely.
                - If results are insufficient, respond with: "Insufficient data".
                - Return ONLY the final answer.

                Final Answer:
         """
       )
       self.chain = self.collector_prompt | self.llm | self.parser

    def collect(self, question, results):
        return self.chain.invoke(question=question, results=results)