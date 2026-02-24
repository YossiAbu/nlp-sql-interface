# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NLP-to-SQL interface: users type natural language questions, the backend converts them to SQL via LangChain + OpenAI, executes against a PostgreSQL database of FC 25 (FIFA) player data, and returns formatted results.

## Commands

### Backend (from `backend/`)
```bash
# Run server
python -m uvicorn main:app --reload          # http://localhost:8000

# Tests (uses .env.test automatically via conftest.py)
pytest                                        # all tests
pytest tests/test_query.py -v                 # single file
pytest --cov=services --cov=models --cov=main --cov-report=term-missing

# Load FIFA player data into DB
python load_data.py

# Model validation (costs money - calls real OpenAI API)
python tests/validate_model.py
```

### Frontend (from `frontend-app/`)
```bash
npm run dev          # Vite dev server on http://localhost:5173
npm run build        # production build
npm run lint         # ESLint
npm run test         # Vitest (watch mode)
npm run test:run     # Vitest (single run)
npm run test:e2e     # Playwright (stop dev backend first)
```

### Docker
```bash
docker-compose up    # from project root - starts postgres, backend, frontend
```

## Architecture

### Request Flow
1. Frontend (`lib/api.ts`) sends POST `/query` with `{ question }` to FastAPI backend
2. `main.py` validates input (length, suspicious patterns), rate-limits (20/min/IP)
3. `query_service.handle_query()` applies alias mapping (e.g., "club" -> "team"), builds a schema-aware prompt with dataset description and SQL guidelines, then calls `ai_service.get_db_chain()` (LangChain `SQLDatabaseChain`)
4. The chain generates SQL, which is extracted/cleaned from intermediate steps, validated (SELECT-only), and executed against PostgreSQL via LangChain's `SQLDatabase`
5. Results are formatted as `QueryResponse` and optionally saved to `history` table if user is authenticated

### Backend Structure (`backend/`)
- **`main.py`** - FastAPI app with all routes: `/query`, `/schema`, `/health`, `/login`, `/register`, `/history`, etc.
- **`services/ai_service.py`** - LangChain `SQLDatabaseChain` setup using `ChatOpenAI`. Currently uses OpenAI models via LangChain.
- **`services/query_service.py`** - Core NLP-to-SQL logic: alias mapping, prompt building (dataset description + SQL guidelines), SQL extraction/cleaning, result formatting. This is the most complex file.
- **`services/db_service.py`** - Dual DB access: SQLAlchemy sessions (for ORM/history) and LangChain `SQLDatabase` (for AI chain)
- **`services/engine_factory.py`** - Singleton engine factory with connection pooling (`QueuePool`)
- **`services/auth_service.py`** - Cookie-based auth (`user_id` cookie), FastAPI dependencies `require_user`/`optional_user`
- **`services/user_service.py`** - User CRUD with bcrypt password hashing, uses raw SQLAlchemy Core (not ORM)
- **`services/history_service.py`** - Query history CRUD using SQLAlchemy ORM
- **`models/history.py`** - SQLAlchemy ORM models (`User`, `History`) with `declarative_base`
- **`models/request_models.py`** / **`models/response_models.py`** - Pydantic v2 request/response schemas
- **`config/logging_config.py`** - Structured logging setup

### Frontend Structure (`frontend-app/`)
- React 19 + TypeScript + Vite + TailwindCSS 4
- **Pages**: `QueryInterface` (main), `History`, `Login`, `Register`
- **`lib/api.ts`** - API client with `fetch()` + credentials
- **`contexts/AuthContext.tsx`** - Auth state management
- UI components from Radix UI + shadcn/ui pattern

### Database
- PostgreSQL 15. Single `players` table (FC 25 dataset loaded from `data/male_players.csv` via `load_data.py`)
- `users` and `history` tables created by SQLAlchemy on startup (`init_db()`)

### Testing
- Backend tests auto-mock the AI chain and schema via `conftest.py` `mock_services` fixture (autouse). Use `@pytest.mark.no_mock` to skip mocking.
- `@pytest.mark.real_db` marks tests that need a populated database (auto-skipped in CI).
- Tests use `.env.test` with a separate `nlp_sql_test` database.
- Frontend uses Vitest + React Testing Library + happy-dom.

## Environment Variables (`backend/.env`)
- `DATABASE_URL` - PostgreSQL connection string (required)
- `OPENAI_API_KEY` - OpenAI API key (required for AI features)
- `OPENAI_MODEL` - Model name, default `gpt-4o-mini`
- `FRONTEND_URL` - Production frontend URL for CORS (optional)

## Refactor Direction
- Clean all legacy OpenAI usage -> pure Anthropic patterns
- Make code as short and readable as possible (remove duplication, unnecessary abstractions)
- Optimize for performance (caching, efficient DB queries, async where possible)
- Keep all existing functionality + tests must pass
- Use modern Python (type hints, pydantic v2, structured logging)
- Follow Anthropic best practices for LLM integration
- After every major change: run tests and fix failures automatically
