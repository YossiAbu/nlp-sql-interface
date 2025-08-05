import ast
import re
import time
from typing import Any, Dict, List
from .ai_service import get_db_chain
from .schema_service import get_schema_text
from .db_service import get_db
from .logging_service import logger
from models.response_models import QueryResponse

# ---------------- Alias Mapping ----------------
ALIASES: Dict[str, str] = {
    # Table
    "footballers": "players",
    "soccer players": "players",
    "fifa players": "players",

    # Common column synonyms
    "overall": "ovr",
    "overall rating": "ovr",
    "rating": "ovr",
    "pace": "pac",
    "shooting": "sho",
    "passing": "pas",
    "dribbling": "dri",
    "physical": "phy",
    "position name": "position",
    "team name": "team",
    "club": "team",
    "nationality": "nation",
    "country": "nation",
    "league name": "league"
}

def apply_alias_mapping(text: str) -> str:
    """Replace user-friendly terms with DB terms (case-insensitive)."""
    result = text
    for alias, actual in ALIASES.items():
        result = re.sub(rf"\b{re.escape(alias)}\b", actual, result, flags=re.IGNORECASE)
    return result

# ---------------- Dataset Description ----------------
DATASET_DESCRIPTION: str = """
The dataset provides comprehensive information on FC 25 players, focusing on their in-game ratings, attributes, and additional statistics.
It is derived from the EA SPORTS Website using web scraping.

Here’s a breakdown of the main columns:

Rank: Player’s ranking based on overall rating (OVR) within the FC 25 group.
Name: The full name of the player.
Height: The player’s height.
Weight: The player’s weight.
Position: The primary position the player plays on the field.
Alternative positions: Other positions the player can play effectively.
Age: The player’s age.
Nation: The country the player represents.
League: The football league where the player currently plays.
Team: The club team the player is part of.
Play style: Specific gameplay traits.

Player Attributes: Acceleration, Sprint Speed, Positioning, Finishing, Shot Power, Long Shots, Volleys, Penalties.
Passing and Vision: Vision, Crossing, Free Kick Accuracy, Short Passing, Long Passing, Curve.
Dribbling and Agility: Dribbling, Agility, Balance, Reactions, Ball Control.
Mentality and Defense: Composure, Interceptions, Heading Accuracy, Defensive Awareness, Standing Tackle, Sliding Tackle.
Physical Attributes: Jumping, Stamina, Strength, Aggression.
Technical Skills: Weak foot, Skill moves, Preferred foot.
Goalkeeping Attributes: GK Diving, GK Handling, GK Kicking, GK Positioning, GK Reflexes.
"""

# ---------------- Prompt Builder ----------------
def build_schema_aware_prompt(question: str, schema_text: str) -> str:
    """Build schema & dataset-aware prompt for AI."""
    return (
        f"{question}\n\n"
        "Here is the database schema:\n"
        f"{schema_text}\n\n"
        "Here is a detailed description of each column:\n"
        f"{DATASET_DESCRIPTION}\n\n"
        "Only write a valid SQL SELECT query using the tables and columns listed above."
    )

# ---------------- Helper Functions ----------------
def format_raw_rows(raw_result: List[Any], column_names: List[str]) -> List[Dict[str, Any]]:
    """Format raw DB rows into list of dicts."""
    if not raw_result or not column_names:
        return []
    return [
        {column_names[i]: value for i, value in enumerate(row) if i < len(column_names)}
        for row in raw_result
    ]

def extract_sql_query(result_dict: Dict[str, Any]) -> str:
    """Extract SQL query from AI intermediate steps."""
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

def extract_raw_results(result_dict: Dict[str, Any], sql_query: str) -> List[Any]:
    """Extract raw query results from AI output or run SQL directly."""
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

def extract_column_names(sql_query: str) -> List[str]:
    """Extract column names from SQL query."""
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
    """Process user question and return SQL + results."""
    start_time = time.time()
    logger.info(f"Received question: {question}")

    # Apply alias mapping
    mapped_question = apply_alias_mapping(question)
    if mapped_question != question:
        logger.info(f"Alias mapping applied. Transformed question: {mapped_question}")
    question = mapped_question

    # Get cached schema for prompt
    schema_text = get_schema_text()

    # Build schema & dataset-aware prompt
    prompt_with_schema = build_schema_aware_prompt(question, schema_text)

    # First attempt
    db_chain = get_db_chain()
    result = db_chain.invoke(prompt_with_schema)
    sql_query = extract_sql_query(result)
    retried = False

    # Retry if invalid
    if not sql_query or not sql_query.strip().upper().startswith("SELECT"):
        logger.warning("First attempt failed to produce valid SELECT SQL. Retrying...")
        retried = True
        result = db_chain.invoke(prompt_with_schema)
        sql_query = extract_sql_query(result)

    execution_time = int((time.time() - start_time) * 1000)

    # Final validation
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

    # Execute query
    raw_db_result = extract_raw_results(result, sql_query)
    column_names = extract_column_names(sql_query)
    formatted_rows = format_raw_rows(raw_db_result, column_names)

    if retried:
        logger.info("✅ Retry successful")
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
