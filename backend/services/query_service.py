import ast
import re
import time
from .ai_service import get_db_chain
from .schema_service import get_schema_text
from .db_service import get_db
from .logging_service import logger
from models.response_models import QueryResponse

# ---------------- Helper Functions ----------------
def format_raw_rows(raw_result, column_names):
    if not raw_result or not column_names:
        return []
    return [
        {column_names[i]: value for i, value in enumerate(row) if i < len(column_names)}
        for row in raw_result
    ]

def extract_sql_query(result_dict):
    intermediate_steps = result_dict.get("intermediate_steps", [])
    for step in intermediate_steps:
        if isinstance(step, str):
            if "SELECT" in step.upper() and "FROM" in step.upper():
                lines = step.split('\n')
                sql_lines, capturing = [], False
                for line in lines:
                    if "SELECT" in line.upper():
                        capturing = True
                    if capturing:
                        sql_lines.append(line.strip())
                        if line.strip().endswith(';'):
                            break
                if sql_lines:
                    return ' '.join(sql_lines).rstrip(';')
        elif isinstance(step, dict) and 'sql_cmd' in step:
            return step['sql_cmd']
    sql_pattern = r'SQLQuery:\s*(SELECT.*?(?:LIMIT\s+\d+)?)\s*;?\s*(?=SQLResult:|$)'
    sql_match = re.search(sql_pattern, str(result_dict), re.IGNORECASE | re.DOTALL)
    if sql_match:
        return ' '.join(sql_match.group(1).strip().split())
    return ""

def extract_raw_results(result_dict, sql_query):
    intermediate_steps = result_dict.get("intermediate_steps", [])
    for step in intermediate_steps:
        if isinstance(step, str):
            if step.startswith('[') and step.endswith(']'):
                try:
                    return ast.literal_eval(step)
                except:
                    pass
            if "SQLResult:" in step:
                try:
                    return ast.literal_eval(step.split("SQLResult:")[-1].strip())
                except:
                    pass
    if sql_query:
        try:
            raw_result = get_db().run(sql_query)
            return ast.literal_eval(raw_result) if raw_result else []
        except Exception as e:
            logger.error(f"Error executing query directly: {e}")
    return []

def extract_column_names(sql_query):
    if not sql_query:
        return ["rank", "name", "ovr", "position", "nation", "team"]
    try:
        match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_query, re.IGNORECASE | re.DOTALL)
        if not match:
            return ["rank", "name", "ovr", "position", "nation", "team"]
        select_part = match.group(1).strip()
        if select_part.strip() == '*':
            return ["rank", "name", "ovr", "position", "nation", "team"]
        columns = []
        for col in select_part.split(','):
            col = col.strip().strip('"\'')
            if ' as ' in col.lower():
                col = col.split(' as ')[-1].strip()
            if '.' in col:
                col = col.split('.')[-1]
            columns.append(col)
        return columns or ["rank", "name", "ovr", "position", "nation", "team"]
    except Exception as e:
        logger.error(f"Error parsing column names: {e}")
        return ["rank", "name", "ovr", "position", "nation", "team"]

# ---------------- Main Query Handling ----------------
def handle_query(question: str) -> QueryResponse:
    start_time = time.time()
    logger.info(f"Received question: {question}")

    schema_text = get_schema_text()
    prompt_with_schema = (
        f"{question}\n\n"
        "Here is the database schema:\n"
        f"{schema_text}\n\n"
        "Only write a valid SQL SELECT query using the tables and columns listed above."
    )

    db_chain = get_db_chain()
    result = db_chain.invoke(prompt_with_schema)
    sql_query = extract_sql_query(result)
    retried = False

    if not sql_query or not sql_query.strip().upper().startswith("SELECT"):
        logger.warning("First attempt failed. Retrying with schema...")
        retried = True
        result = db_chain.invoke(prompt_with_schema)
        sql_query = extract_sql_query(result)

    execution_time = int((time.time() - start_time) * 1000)

    if not sql_query:
        return QueryResponse(
            sql_query="",
            results="",
            raw_rows=[],
            status="error",
            execution_time=execution_time,
            error_message="The AI could not generate a valid SQL query even after retry."
        )

    if not sql_query.strip().upper().startswith("SELECT"):
        return QueryResponse(
            sql_query=sql_query,
            results="",
            raw_rows=[],
            status="error",
            execution_time=execution_time,
            error_message="Only SELECT queries are allowed."
        )

    raw_db_result = extract_raw_results(result, sql_query)
    column_names = extract_column_names(sql_query)
    formatted_rows = format_raw_rows(raw_db_result, column_names)

    if retried:
        logger.info("✅ Retry with schema successful")
    logger.info("SQLQuery:\n" + sql_query.strip())
    logger.info(f"Execution time: {execution_time} ms")
    logger.info(f"Returned {len(formatted_rows)} rows")

    return QueryResponse(
        sql_query=sql_query,
        results=result.get("result", ""),
        raw_rows=formatted_rows,
        status="success",
        execution_time=execution_time
    )
