# LLM Chat With Databse
This project demonstrates how to use a large language model (LLM) to interact with a databse.
 
 ### - use gemini-2.5-flash to create SQL query based on user input and database schema
 ### - use engine to execute the SQL query and return the result
 ### - use gemini-2.5-flash to generate a response based on the query result and user input
 

## Installation
1. install the required packages using pip:
```bash     
   pip install -r requirements.txt
   ```

## Set up environment variables
1. get copy the .env.example file to .env and fill in the values for GOOGLE_API_KEY and DB_URL.
```bash
   cp .env.example .env
   ```

## upload the database into cloud database provider like railway ,
- run the deploy.py file 
```bash
   python Chinhook/deploy.py
   ```

## Deploy the app using streamlit.
```bash
   streamlit run llm_chat_with_db.py
   ```