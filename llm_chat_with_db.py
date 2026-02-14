import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_URL = os.getenv("DB_URL")

llm = ChatGoogleGenerativeAI( model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
parser = StrOutputParser()

# connect to the database.
@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

# fetch the database schema and format it as a string to be used in the prompt. 
@st.cache_resource
def get_schema():
    engine = get_engine()
    inspector_query = text("""
                        select table_name, column_name
                        from information_schema.columns 
                        where table_schema = 'public'   
                        order by table_name, ordinal_position;          
                        """
                        )  
    schema_str = ""
    try:
        with engine.connect() as conn:
            result = conn.execute(inspector_query) 
            current_table = ""
            for row in result :
                table_name, column_name = row[0], row[1]
                if table_name != current_table :
                    schema_str += f"\nTable : {table_name}\n Columns: "
                    current_table = table_name
                schema_str += f"{column_name}, "    
    except Exception as e:
        st.error(f"an error accur {e} ")

    return schema_str

# the first llm chain to generate sql query based on user question and database schema.
sql_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template="""
    you are an expert postgressSQL data analyst.
    here is the database schema {schema}.
    Your task:
    1- Write a postgressSQl query to answer the following question {question}
    2- Important : the tables were created via pandas.
              - if columns are Mixescase, use double quotes around them in the query.
    3- ONLY return the sql query , without any explanation or comments   
    4- If date columns are stored as TEXT, cast them explicitly using ::DATE or ::TIMESTAMP   
    5- If you are not sure about the question, write a query that can help you understand the question better by exploring the data.    
    
    CRITICAL RULE (MANDATORY):
        For any column representing names (e.g., Name, FirstName, LastName, ArtistName):

        - You MUST use ILIKE with '%' wildcards.
        - You MUST NOT use equality (=) unless the question explicitly says "exact match".
        - If you use "=" for names without explicit exact match instruction, the query is WRONG.
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


# Streamlit UI

st.set_page_config(page_title="Postgress SQL")
st.title("Chat With DB")

question = st.text_input("Ask a question about your database")

if question:
    schema = get_schema()

    sql_query = get_sql_chain.invoke({
        "schema": schema,
        "question": question
    })
    sql_query = clean_sql(sql_query)

    st.subheader("Generated SQL")
    st.code(sql_query, language="sql")

    data = run_query(sql_query)

    if isinstance(data, pd.DataFrame):
        st.subheader("Query Result")
        st.dataframe(data)

        answer = nature_response_chain.invoke({
            "question": question,
            "sql": sql_query,
            "data": data.to_dict()
        })

        st.subheader("Answer")
        st.write(answer)
    else:
        st.error(data)