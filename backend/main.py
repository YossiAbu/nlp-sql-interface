from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.request_models import QueryRequest
from models.response_models import QueryResponse, SchemaResponse
from services.query_service import handle_query
from services.schema_service import get_schema_response, refresh_schema_cache

app: FastAPI = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query", response_model=QueryResponse)
async def process_query(payload: QueryRequest) -> QueryResponse:
    """Process a natural language question and return SQL + results."""
    return handle_query(payload.question)

@app.get("/schema", response_model=SchemaResponse)
async def get_schema() -> SchemaResponse:
    """Return the current database schema in structured JSON."""
    return get_schema_response()

@app.get("/refresh-schema", response_model=SchemaResponse)
async def refresh_schema() -> SchemaResponse:
    """Refresh schema cache and return updated database schema."""
    return refresh_schema_cache()
