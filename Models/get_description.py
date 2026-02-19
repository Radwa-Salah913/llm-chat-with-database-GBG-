import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
load_dotenv()


def get_description(schema: str, llm) -> str:
    
    parser = StrOutputParser()

    prompt = PromptTemplate(
        input_variables=["schema"], 
        template="""
        you are an expert postgressSQL data analyst.
        here is the database schema contain tables name, columns name, data type for each column and, an example value for each column in the schema: {schema}.
        Your task:
        1- Write a concise description of the database for each column in each table in 2-3 sentences.
        2- The description should be based on the column name, data type and the example value provided in the schema.
        3- The description should be concise and informative, it should give a clear idea about the content"""
        )

    description_chain = prompt | llm | parser
    description = description_chain.invoke({
        "schema": schema
    })
    return description

