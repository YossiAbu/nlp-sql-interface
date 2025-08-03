from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import time
import ast
import re

from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.utilities import SQLDatabase
from langchain_core.runnables import Runnable

# Load env vars
load_dotenv()
# Load OpenAI key and DB URL
openai_api_key = os.getenv("OPENAI_API_KEY")
postgres_url = os.getenv("POSTGRESQL_URL")

# 1. Connect to your PostgreSQL database
db = SQLDatabase.from_uri(postgres_url)
# 2. Setup LLM
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=openai_api_key)
# 3. Build the SQL chain
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, return_intermediate_steps=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_raw_rows(raw_result, column_names):
    """Convert raw database tuples to list of dictionaries"""
    if not raw_result or not column_names:
        return []
    
    formatted_rows = []
    for row in raw_result:
        row_dict = {}
        for i, value in enumerate(row):
            if i < len(column_names):
                row_dict[column_names[i]] = value
        formatted_rows.append(row_dict)
    
    return formatted_rows

def extract_sql_query(result_dict):
    """Extract SQL query from the chain result"""
    # Try to get from intermediate steps first
    intermediate_steps = result_dict.get("intermediate_steps", [])
    
    for step in intermediate_steps:
        if isinstance(step, str):
            # Look for complete SQL query in string
            if "SELECT" in step.upper() and "FROM" in step.upper():
                # Try to extract complete SQL query
                lines = step.split('\n')
                sql_lines = []
                capturing = False
                for line in lines:
                    if "SELECT" in line.upper():
                        capturing = True
                    if capturing:
                        sql_lines.append(line.strip())
                        if line.strip().endswith(';'):
                            break
                if sql_lines:
                    return ' '.join(sql_lines).rstrip(';')
        elif isinstance(step, dict):
            # Check if it's a SQL command step
            if 'sql_cmd' in step:
                return step['sql_cmd']
    
    # If not found in intermediate steps, try to extract from the full result string
    full_result_str = str(result_dict)
    
    # Look for SQLQuery: pattern with better regex
    sql_pattern = r'SQLQuery:\s*(SELECT.*?(?:LIMIT\s+\d+)?)\s*;?\s*(?=SQLResult:|$)'
    sql_match = re.search(sql_pattern, full_result_str, re.IGNORECASE | re.DOTALL)
    if sql_match:
        sql_query = sql_match.group(1).strip()
        # Clean up any extra whitespace and newlines
        sql_query = ' '.join(sql_query.split())
        return sql_query
    
    return ""

def extract_raw_results(result_dict, sql_query):
    """Extract raw database results"""
    # First try to get from intermediate steps
    intermediate_steps = result_dict.get("intermediate_steps", [])
    
    for step in intermediate_steps:
        if isinstance(step, str):
            # Look for tuple-like results
            if step.startswith('[') and step.endswith(']'):
                try:
                    return ast.literal_eval(step)
                except:
                    pass
            # Look for SQLResult pattern
            if "SQLResult:" in step:
                result_part = step.split("SQLResult:")[-1].strip()
                try:
                    return ast.literal_eval(result_part)
                except:
                    pass
    
    # If not found in steps, execute the query directly
    if sql_query:
        try:
            raw_result = db.run(sql_query)
            if raw_result:
                try:
                    return ast.literal_eval(raw_result)
                except:
                    pass
        except Exception as e:
            print(f"Error executing query directly: {e}")
    
    return []

def extract_column_names(sql_query):
    """Extract column names from SQL SELECT statement"""
    if not sql_query:
        return ["rank", "name", "ovr", "position", "nation", "team"]  # Default fallback
    
    try:
        # Find the SELECT part
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_query, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return ["rank", "name", "ovr", "position", "nation", "team"]  # Default fallback
        
        select_part = select_match.group(1).strip()
        
        # Handle SELECT *
        if select_part.strip() == '*':
            return ["rank", "name", "ovr", "position", "nation", "team"]  # Default columns
        
        # Split by comma and clean up column names
        columns = []
        for col in select_part.split(','):
            col = col.strip()
            # Remove quotes
            col = col.strip('"\'')
            # If it has an alias (AS keyword), take the alias
            if ' as ' in col.lower():
                col = col.split(' as ')[-1].strip()
            # If it has table prefix, remove it
            if '.' in col:
                col = col.split('.')[-1]
            columns.append(col)
        
        return columns if columns else ["rank", "name", "ovr", "position", "nation", "team"]
    except Exception as e:
        print(f"Error parsing column names: {e}")
        return ["rank", "name", "ovr", "position", "nation", "team"]  # Default fallback

@app.post("/query")
async def process_query(request: Request):
    data = await request.json()
    question = data.get("question")
    
    start_time = time.time()

    try:
        # Use `invoke()` to get both SQL query and result
        result = db_chain.invoke(question)
        
        execution_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        # Extract SQL query
        sql_query = extract_sql_query(result)
        
        # Extract raw results
        raw_db_result = extract_raw_results(result, sql_query)
        
        # Extract column names from SQL query
        column_names = extract_column_names(sql_query)
        
        # Format raw rows as list of dictionaries
        formatted_raw_rows = format_raw_rows(raw_db_result, column_names)

        return {
            "sql_query": sql_query,
            "results": result.get("result", ""),  # Human-readable answer
            "raw_rows": formatted_raw_rows,  # Formatted raw rows from DB
            "status": "success",
            "execution_time": execution_time
        }

    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        print(f"Error processing query: {e}")
        return {
            "sql_query": "",
            "results": "",
            "raw_rows": [],
            "status": "error",
            "execution_time": execution_time,
            "error_message": str(e)
        }