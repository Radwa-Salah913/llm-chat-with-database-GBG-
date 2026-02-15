import streamlit as st
from Controllers.SQLGenerator import SQLGenerator
from Controllers.ResponseGenerator import ResponseGenerator
from Models.run_query import run_query
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

st.set_page_config(page_title="Postgress SQL Chatbot")
st.title("Chat With DB")


question = st.text_input("Ask a question about your database")

if question:
    
    cleaned_sql_query = SQLGenerator().generate_sql(question)
    
    st.subheader("Generated SQL")
    st.code(cleaned_sql_query, language="sql")

    data = run_query(cleaned_sql_query)

    if isinstance(data, pd.DataFrame):
        st.subheader("Query Result")
        st.dataframe(data)

        answer = ResponseGenerator().generate_natural_response(question, cleaned_sql_query, data)

        st.subheader("Answer")
        st.write(answer)
    else:
        st.error(data)