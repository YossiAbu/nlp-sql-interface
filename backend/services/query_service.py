from datetime import datetime
import re
import time
from typing import Any, Dict, List
from .ai_service import generate_sql, get_current_model
from .schema_service import get_schema_text
from .db_service import execute_raw_sql
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

    Here's a breakdown of the main columns:

    Rank: Player's ranking based on overall rating (OVR) within the FC 25 group.
    Name: The full name of the player.
    Height: The player's height.
    Weight: The player's weight.
    Position: The primary position the player plays on the field.
    Alternative positions: Other positions the player can play effectively.
    Age: The player's age.
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

# ---------------- SQL Query Guidelines ----------------
SQL_GUIDELINES: str = """
IMPORTANT SQL QUERY GUIDELINES:

⚠️ CRITICAL DEFAULTS:
- ALWAYS use LIMIT 10 as default (NOT 5, NOT 20, use exactly 10)
- ALWAYS include these 5 columns: rank, name, ovr, position, team

1. POSITION FILTERING:
   - Position values are ABBREVIATIONS (e.g., 'ST', 'CB', 'LW', 'CM')
   - For defenders: Use position LIKE '%CB%' OR position LIKE '%LB%' OR position LIKE '%RB%'
   - For midfielders: Use position LIKE '%CM%' OR position LIKE '%CDM%' OR position LIKE '%CAM%'
   - For forwards: Use position LIKE '%ST%' OR position LIKE '%CF%' OR position LIKE '%LW%' OR position LIKE '%RW%'
   - For wingers: Use position LIKE '%LW%' OR position LIKE '%RW%' OR position LIKE '%LM%' OR position LIKE '%RM%'
   - For goalkeepers: Use position = 'GK'

2. TEAM AND LEAGUE NAMES:
   - Team names often have variations (e.g., 'FC Barcelona', 'Barcelona B', 'Barcelona')
   - Always use LIKE for team/league matching: team LIKE '%Barcelona%' NOT team = 'Barcelona'
   - League names: league LIKE '%Premier League%' NOT league = 'Premier League'

3. PLAYER ROLES:
   - Don't filter by stat attributes (def, pac, sho) when looking for positions
   - Filter by the 'position' column using correct abbreviations

4. "TALLEST/BEST IN EACH POSITION" QUERIES:
   - For "tallest/best/top player in each position/group" queries
   - Use DISTINCT ON (PostgreSQL): SELECT DISTINCT ON (position) ... ORDER BY position, height DESC
   - OR use window functions: ROW_NUMBER() OVER (PARTITION BY position ORDER BY height DESC)
   - DON'T use: WHERE height IN (SELECT MAX(height) ... GROUP BY position) ❌ This is WRONG!

5. COLUMN SELECTION - MANDATORY COLUMNS (VERY IMPORTANT):
   - ALWAYS include these 5 mandatory columns: rank, name, ovr, position, team
   - Add up to 3 additional relevant columns based on the question
   - Maximum 8 columns total (5 mandatory + 3 optional)
   - Order: mandatory columns first, then relevant columns

6. LIMIT CLAUSE (VERY IMPORTANT - READ CAREFULLY):
   - DEFAULT IS 10: Always use LIMIT 10 unless user explicitly asks for different amount
   - DO NOT use LIMIT 5 - this is wrong! Use LIMIT 10 as default
   - Maximum LIMIT: 50 (NEVER exceed this, even if user asks for more)
   - User specifies number: Respect it but cap at 50
   - NO LIMIT clause specified: Add LIMIT 10

   Examples:
   - No specific amount asked → LIMIT 10 (NOT 5!)
   - "top 20 players" → LIMIT 20
   - "top 100 players" → LIMIT 50 (capped at maximum)
   - "show players" → LIMIT 10 (default)

EXAMPLES WITH MANDATORY COLUMNS:
- "Show defenders" →
  SELECT rank, name, ovr, position, team, def, heading_accuracy
  FROM players
  WHERE position LIKE '%CB%' OR position LIKE '%LB%' OR position LIKE '%RB%'
  ORDER BY ovr DESC LIMIT 10

- "Find midfielders" →
  SELECT rank, name, ovr, position, team, pas, vision
  FROM players
  WHERE position LIKE '%CM%' OR position LIKE '%CDM%' OR position LIKE '%CAM%'
  LIMIT 10

- "Fastest players" →
  SELECT rank, name, ovr, position, team, pac, sprint_speed, acceleration
  FROM players
  ORDER BY pac DESC LIMIT 10

- "Players from Barcelona" →
  SELECT rank, name, ovr, position, team, age, nation
  FROM players
  WHERE team LIKE '%Barcelona%'
  LIMIT 10

- "Premier League players" →
  SELECT rank, name, ovr, position, team, league, age
  FROM players
  WHERE league LIKE '%Premier League%'
  LIMIT 10

- "Tallest player in each position" →
  SELECT DISTINCT ON (position) rank, name, ovr, position, team, height
  FROM players
  ORDER BY position, height DESC

- "Best player in each team" →
  SELECT DISTINCT ON (team) rank, name, ovr, position, team
  FROM players
  ORDER BY team, ovr DESC

- "Top 20 players" →
  SELECT rank, name, ovr, position, team
  FROM players
  ORDER BY ovr DESC LIMIT 20

- "Top 100 players" →
  SELECT rank, name, ovr, position, team
  FROM players
  ORDER BY ovr DESC LIMIT 50
  (Note: Capped at 50 even though user asked for 100)
"""

# ---------------- Prompt Builder ----------------
def build_schema_aware_prompt(schema_text: str) -> str:
    """Build schema & dataset-aware system prompt for AI."""
    return (
        "You are a SQL query generator. Given a natural language question about FC 25 football players, "
        "return ONLY a valid PostgreSQL SELECT query. No explanation, no markdown, no code blocks.\n\n"
        "Here is the database schema:\n"
        f"{schema_text}\n\n"
        "Here is a detailed description of each column:\n"
        f"{DATASET_DESCRIPTION}\n\n"
        f"{SQL_GUIDELINES}\n\n"
        "Only write a valid SQL SELECT query using the tables and columns listed above. "
        "Follow the SQL guidelines above for position filtering and team/league name matching. "
        "IMPORTANT: Always use LIMIT 10 as default (not 5, not 20 - exactly 10). "
        "IMPORTANT: Always include mandatory columns: rank, name, ovr, position, team. "
        "Do not place a semicolon before the LIMIT clause. Only use a semicolon at the very end of the SQL statement. "
        "Return ONLY the SQL query without any markdown formatting, code blocks, or extra text."
    )

# ---------------- Helper Functions ----------------
def clean_sql_query(sql_text: str) -> str:
    """Clean SQL query by removing markdown formatting and extra text."""
    if not sql_text:
        return ""

    # Remove markdown code block markers
    sql_text = re.sub(r'```sql\s*', '', sql_text, flags=re.IGNORECASE)
    sql_text = re.sub(r'```\s*$', '', sql_text, flags=re.MULTILINE)
    sql_text = re.sub(r'```', '', sql_text)

    # Remove SQLQuery: prefix if present
    sql_text = re.sub(r'^SQLQuery:\s*', '', sql_text, flags=re.IGNORECASE | re.MULTILINE)

    # Extract SQL query using multiple patterns
    patterns = [
        # Pattern 1: Look for SELECT...FROM pattern
        r'(SELECT\s+.*?FROM\s+.*?)(?:;|\s*$)',
        # Pattern 2: More comprehensive SELECT pattern
        r'(SELECT\s+(?:DISTINCT\s+ON\s*\([^)]+\)\s+)?.*?FROM\s+.*?(?:WHERE\s+.*?)?(?:GROUP\s+BY\s+.*?)?(?:ORDER\s+BY\s+.*?)?(?:LIMIT\s+\d+)?)\s*;?',
    ]

    for pattern in patterns:
        match = re.search(pattern, sql_text, re.IGNORECASE | re.DOTALL)
        if match:
            sql_query = match.group(1).strip()
            # Clean up any remaining artifacts
            sql_query = re.sub(r'\s+', ' ', sql_query)  # Normalize whitespace
            return sql_query

    # If no patterns match, return cleaned text
    return sql_text.strip()

def format_raw_rows(raw_result: List[Any], column_names: List[str]) -> List[Dict[str, Any]]:
    """Format raw DB rows into list of dicts."""
    if not raw_result or not column_names:
        return []
    return [
        {column_names[i]: value for i, value in enumerate(row) if i < len(column_names)}
        for row in raw_result
    ]

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
    current_model = get_current_model()
    logger.info(f"Received question: {question} | Using model: {current_model}")

    # Apply alias mapping
    mapped_question = apply_alias_mapping(question)
    if mapped_question != question:
        logger.info(f"Alias mapping applied. Transformed question: {mapped_question}")
    question = mapped_question

    # Build schema-aware system prompt
    schema_text = get_schema_text()
    system_prompt = build_schema_aware_prompt(schema_text)

    # Generate SQL via OpenAI
    raw_sql = generate_sql(system_prompt, question)
    sql_query = clean_sql_query(raw_sql)
    retried = False

    # Retry if invalid
    if not sql_query or not sql_query.strip().upper().startswith("SELECT"):
        logger.warning("First attempt failed to produce valid SELECT SQL. Retrying...")
        retried = True
        raw_sql = generate_sql(system_prompt, question)
        sql_query = clean_sql_query(raw_sql)

    execution_time = int((time.time() - start_time) * 1000)

    # Final validation
    if not sql_query:
        return QueryResponse(
            sql_query="",
            results="",
            raw_rows=[],
            status="error",
            execution_time=execution_time,
            error_message="The AI could not generate a valid SQL query even after retry.",
            created_date=datetime.utcnow()
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

    # Add LIMIT clause if missing
    if "LIMIT" not in sql_query.upper():
        sql_query = sql_query.rstrip(';').strip() + " LIMIT 20"
        logger.info("Added LIMIT 20 clause to query to prevent token overflow")

    # Execute query directly
    try:
        raw_db_result = execute_raw_sql(sql_query)
    except Exception as e:
        logger.error(f"SQL execution error: {e}")
        return QueryResponse(
            sql_query=sql_query,
            results="",
            raw_rows=[],
            status="error",
            execution_time=int((time.time() - start_time) * 1000),
            error_message=f"SQL execution failed: {e}",
            created_date=datetime.utcnow()
        )

    column_names = extract_column_names(sql_query)
    formatted_rows = format_raw_rows(raw_db_result, column_names)

    # Limit results to 20 rows
    MAX_ROWS = 20
    if len(formatted_rows) > MAX_ROWS:
        logger.info(f"Limiting results from {len(formatted_rows)} rows to {MAX_ROWS} rows")
        formatted_rows = formatted_rows[:MAX_ROWS]

    if retried:
        logger.info("Retry successful")
    logger.info(f"Model: {current_model}")
    logger.info("SQLQuery:\n" + sql_query.strip())
    logger.info(f"Execution time: {execution_time} ms")
    logger.info(f"Returned {len(formatted_rows)} rows")

    return QueryResponse(
        sql_query=sql_query,
        results=f"Query returned {len(formatted_rows)} rows",
        raw_rows=formatted_rows,
        status="success",
        execution_time=execution_time,
        created_date=datetime.utcnow(),
    )
