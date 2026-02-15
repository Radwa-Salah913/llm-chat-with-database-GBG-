from sqlalchemy import create_engine, text
from Models.get_schema import  get_engine
import pandas as pd

def run_query(query):
    engine = get_engine()
    with engine.connect() as conn:  
        try:
            result = conn.execute(text(query))
            return pd.DataFrame(result.fetchall(), columns=result.keys())
        except Exception as e:
            return str(e)