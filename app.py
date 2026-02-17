import streamlit as st
from Controllers.SQLGenerator import SQLGenerator
from Controllers.ResponseGenerator import ResponseGenerator
from Controllers.ComplexityDetector import ComplexityDetector
from Controllers.Decomposer import Decomposition
from Controllers.Collector import Collector
from Models.run_query import run_query
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

st.set_page_config(page_title="Postgress SQL Chatbot")
st.title("Chat With DB")


question = st.text_input("Ask a question about your database")

if question:
    
    status = ComplexityDetector().detect(question=question)
    st.subheader("Generated SQL")

    if status == "SIMPLE":
        cleaned_sql_query = SQLGenerator().generate_sql(question)
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

    else:
        sub_questions = Decomposition().decompose(question)

        st.subheader("Sub-questions")
        results ={}

        for i, sub_q in enumerate(sub_questions):
            st.write(f"{i+1}. {sub_q}")
            cleaned_sql_query = SQLGenerator().generate_sql(sub_q)
            st.code(cleaned_sql_query, language="sql")
            data = run_query(cleaned_sql_query)
            results[f"sub_question_{i}"] = {"question" : sub_q, "sql": cleaned_sql_query, "data": data}

        final_answer = Collector().collect(question, results)
        st.subheader("Final Answer")
        st.write(final_answer)
