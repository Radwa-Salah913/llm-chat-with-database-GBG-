import os
from dotenv import load_dotenv
from Models.get_schema import get_schema, get_engine
from Models.get_description import get_description
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class SQLGenerator:

    def __init__(self):
        load_dotenv()

        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI( model="gemini-2.5-flash", google_api_key=self.GOOGLE_API_KEY,temperature=0.2)
        self.parser = StrOutputParser()

        # get schema + description once
        self.schema = get_schema()
        self.description = get_description(self.schema, self.llm)

        self.sql_prompt = PromptTemplate(
            input_variables=["schema", "question", "description"],
            template="""
            you are an expert postgressSQL data analyst.
            here is the database schema contain tables name, columns name, data type for each column and, 
            an example value for each column in the schema: {schema}.
            here is the description of each column in the database: {description}.
            Your task:
            1- Write ONLY a postgressSQl query to answer the following question: {question}.
            2- Important : the tables were created via pandas.
                    - if columns are Mixescase, use double quotes around them in the query.
                    - write the actualy name of the table in double quotes.
                    - get the columns name and tables name from the provided schema EXACTLY as it is, do not make up any column or table name that is not in the schema.
                    
            3- ONLY return the sql query , without any explanation or comments   
            4- If date columns are stored as TEXT, cast them explicitly using ::DATE or ::TIMESTAMP   
            5- write a query that can help you understand the question better by exploring the data before get the final query.  
        
            CRITICAL RULE (MANDATORY):
            1- For any column representing names (e.g., Name, FirstName, LastName, ArtistName):

                - You MUST use ILIKE with '%' wildcards.
                - You MUST NOT use equality (=) unless the question explicitly says "exact match".
                - If you use "=" for names without explicit exact match instruction, the query is WRONG.

            2- If a question refers to a country name that may have synonyms or abbreviations,
                map the value to the canonical form stored in the database before generating SQL.

                    Example mappings:
                    - United States, United State, US, U.S.A., America → USA
                    - United Kingdom, UK → UK
                    - Germany, Deutschland → Germany

                    Use the database-stored value in the WHERE clause.

                3- Evaluate your generated query based on the above rules, attached schema and, the postgreSQL Syntax, if you find any violation, rewrite the query to fix it.        
                4- GET the columns name and tables name from the provided schema EXACTLY as it is.
            """
        )

        self.chain = self.sql_prompt | self.llm | self.parser

    def generate_sql(self, question: str) -> str:
        sql = self.chain.invoke({
            "schema": self.schema,
            "question": question,
            "description": self.description
        })

        return self.clean_sql(sql)

    @staticmethod
    def clean_sql(sql: str) -> str:
        return (
            sql.replace("```sql", "")
               .replace("```", "")
               .strip()
        )
