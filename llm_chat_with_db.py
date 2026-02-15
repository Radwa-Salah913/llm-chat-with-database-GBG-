import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from Controllers.get_schema import get_schema, get_engine
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI( model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.0)
parser = StrOutputParser()

# the first llm chain to generate sql query based on user question and database schema.
sql_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template="""
    you are an expert postgressSQL data analyst.
    here is the database schema contain tables name, columns name, data type for each column and, 
    an example value for each column in the schema: {schema}.
    Your task:
    1- Write ONLY a postgressSQl query to answer the following question: {question}.
    2- Important : the tables were created via pandas.
              - if columns are Mixescase, use double quotes around them in the query.
              - write the actualy name of the table in double quotes.
              
    3- ONLY return the sql query , without any explanation or comments   
    4- If date columns are stored as TEXT, cast them explicitly using ::DATE or ::TIMESTAMP   
    5- If you are not sure about the question, write a query that can help you understand the question better by exploring the data.  
 
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

        3- Evaluate your generated query based on the above rules, schema and, the postgreSQL Syntax, if you find any violation, rewrite the query to fix it.        
    """
    
)
get_sql_chain = sql_prompt | llm | parser

# clean the llm result to ensure we only have the sql query without any extra text or formatting.
def clean_sql(sql: str) -> str:
    return (
        sql.replace("```sql", "")
           .replace("```", "")
           .strip()
    )

# execute the sql query and return the result as a pandas dataframe.
def run_query(query):
    engine = get_engine()
    with engine.connect() as conn:  
        try:
            result = conn.execute(text(query))
            return pd.DataFrame(result.fetchall(), columns=result.keys())
        except Exception as e:
            return str(e)

# the second llm chain to convert the sql query result into a natural language answer.
nature_response_prompt = PromptTemplate(
    input_variables = ["question", "sql", "data"],
    template="""
            user question: {question}
            sql qery used: {sql}
            data recevied: {data}
            YOUR TASK:
            Answer the user question in a nature language format based on data recevied.
            If the data is empty, say "No results found".
        """
)

nature_response_chain = nature_response_prompt | llm | parser

