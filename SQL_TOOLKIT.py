from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

db = SQLDatabase.from_uri(os.getenv("DB_URL"))
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.0)
toolkit = SQLDatabaseToolkit(db = db, llm = llm)

agent_executor = create_sql_agent(
    llm = llm,
    toolkit = toolkit,
    max_iterations = 15,
    max_execution_time = 60,
    top_k = 3,
    verbose = False
)

error_string = "Could not parse LLM output:"
def run_agent_query(query, agent_executor, error_string):
    try:
        result = agent_executor.invoke(query, return_only_outputs = True)["output"]
    except Exception as e:
        error_message = str(e)
        # Check if the error message contains the specific string
        if error_string in error_message:
            # Extract the part after the specific string and strip backticks
            result = error_message.split(error_string)[1].strip().strip('`')
        else:
            result = f"Error occurred: {error_message}"
    return result



# streamlit app


st.set_page_config(page_title="Postgress SQL Chatbot")
st.title("Chat With DB")


question = st.text_input("Ask a question about your database")

if question:

    result = run_agent_query(question, agent_executor, error_string)
    st.subheader("Answer")
    st.write(result)