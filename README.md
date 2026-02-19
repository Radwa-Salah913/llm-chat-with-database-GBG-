# LLM Chat With Databse
This project demonstrates how to use a large language model (LLM) to interact with a databse.
 
### Features

- Ask questions in natural language about your database.

- Detects whether the question is simple or complex.

- Decomposes complex questions into sub-questions.

- Executes queries on the database.

- Displays query results in tabular format.

- Generates natural language answers from query results.
 
------------------------------------------------------------------------------------------------------

### System Architecture

------> The system is composed of multiple controllers:

#### - ComplexityDetector
Determines whether the user query is SIMPLE or COMPLEX.

#### - SQLGenerator
Generates SQL queries from natural language.

#### - Decomposition
Breaks complex questions into smaller sub-questions.

#### - Collector
Combines answers from sub-questions into a final response.

#### - ResponseGenerator
Converts query results into natural language answers.



------> The system is composed of multiple Models:

#### - run_query
Executes SQL queries on the PostgreSQL database.

#### - get_schema
Retrieves the database schema, including table names, column names, data types, and example values.

#### - get_description
Generates concise descriptions for each column in the database schema based on the column name, data type, and example value.


-----------------------------------------------------------------------------------------------------


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
   streamlit run app.py
   ```

-------------------------------------------------------------------------
### How It Works

- User enters a question about the database.

- The system checks if the question is SIMPLE or COMPLEX.

#### - If SIMPLE:

      - Generate SQL

      - Run SQL

      - Display result

      - Generate final answer

#### - If COMPLEX:

      - Decompose into sub-questions

      - Generate SQL for each

      - Execute queries

      - Collect all results

      - Generate final combined answer

---------------------------------------------------------------------------------------------------

## Alternative Approach: Using LangChain SQL Toolkit Directly

In addition to the multi-step pipeline, this project also supports a direct approach using LangChain’s built-in SQL Agent Toolkit.

### This approach allows the system to:

- Interpret the user’s natural language question.

- Automatically generate and execute SQL queries.

- Return a final answer without explicitly exposing the SQL steps.

## Deploy the app using streamlit.
```bash
streamlit run SQL_TOOLKIT.py
   ```
