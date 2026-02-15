import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import streamlit as st
load_dotenv()

DB_URL = os.getenv("DB_URL")
# connect to the database.
@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

# fetch the database schema (tables name, columns name and, it's data types)and format it as a string to be used in the prompt. 
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
                table_name, column_name, data_type = row[0], row[1], row[2]

                if table_name != current_table :
                    schema_str += f"\nTable : {table_name}\n Columns: "
                    current_table = table_name

                    # get one sample row.
                    sample_query = text(f'SELECT "{column_name}" FROM "{table_name}" LIMIT 1')
                    sample_row = conn.execute(sample_query).fetchone()
                    sample_row = sample_row if sample_row else None

                # Get value for this column from sample row
                sample_value = None
                if sample_row:
                    sample_value = sample_row[column_name]

                schema_str += f"   - {column_name} ({data_type}) | example: {sample_value}\n"  
                 
    except Exception as e:
        print(f"an error accur {e} ")
   
    return schema_str
