from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.request_models import QueryRequest
from models.response_models import QueryResponse, SchemaResponse
from services.query_service import handle_query
from services.schema_service import get_schema_response, get_schema_text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query", response_model=QueryResponse)
async def process_query(payload: QueryRequest):
    return handle_query(payload.question)

@app.get("/schema", response_model=SchemaResponse)
async def get_schema():
    return get_schema_response()

@app.get("/refresh-schema")
async def refresh_schema():
    get_schema_text(force_refresh=True)
    return {"status": "Schema cache refreshed"}
