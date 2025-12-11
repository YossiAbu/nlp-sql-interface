# NLP to SQL Interface 🤖⚡

[![Tests](https://github.com/YossiAbu/nlp-sql-interface/actions/workflows/tests.yml/badge.svg)](https://github.com/YossiAbu/nlp-sql-interface/actions/workflows/tests.yml)

A full-stack application that converts natural language questions into SQL queries using OpenAI's GPT models. Ask questions in plain English and get instant results from your database!

![Architecture](architecture_diagram.png)

## 🌟 Features

- **Natural Language to SQL**: Convert questions like "Show me the top 10 players by rating" into SQL queries automatically
- **Interactive Query Interface**: Modern, responsive UI built with React and TypeScript
- **Query History**: Save and revisit previous queries with search and filtering capabilities
- **Real-time Results**: Instant execution and formatted display of query results
- **Authentication**: Secure user authentication with session management
- **Dark/Light Mode**: Toggle between themes for comfortable viewing
- **Comprehensive Testing**: Unit tests, integration tests, and E2E tests with 100% coverage goals
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Reliable relational database
- **SQLAlchemy** - ORM for database operations
- **OpenAI API** - GPT models for NLP to SQL conversion
- **LangChain** - Framework for LLM application development
- **Pytest** - Testing framework with async support

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Vitest** - Fast unit test framework
- **Playwright** - End-to-end testing
- **React Testing Library** - Component testing utilities

### DevOps
- **GitHub Actions** - CI/CD automation
- **Docker-ready** - Containerization support
- **PostgreSQL Service Containers** - Isolated test databases

## 📋 Prerequisites

- **Python 3.10.8** or higher
- **Node.js 18** or higher
- **PostgreSQL 15** or higher
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YossiAbu/nlp-sql-interface.git
cd nlp-sql-interface
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv nlp-sql-env

# Activate virtual environment
# Windows:
nlp-sql-env\Scripts\activate
# macOS/Linux:
source nlp-sql-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `backend/.env` with your credentials:**
```env
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/nlp_sql
OPENAI_MODEL=gpt-4o-mini
```

### 3. Database Setup

```bash
# Create databases (production and test)
createdb nlp_sql
createdb nlp_sql_test

# Load sample data (FIFA players dataset)
python load_data.py
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend-app

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🎯 Running the Application

### Start Backend Server

```bash
cd backend
# Activate virtual environment first (if not already active)
python -m uvicorn main:app --reload
```

Backend will run on: `http://localhost:8000`

### Start Frontend Development Server

```bash
cd frontend-app
npm run dev
```

Frontend will run on: `http://localhost:5173`

### Access the Application

Open your browser and navigate to `http://localhost:5173`

## 🧪 Testing

### Backend Tests

```bash
cd backend
# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov=models --cov=main --cov-report=term-missing

# Run specific test file
pytest tests/test_query.py -v
```

### Frontend Tests

```bash
cd frontend-app

# Run unit tests
npm run test

# Run tests in watch mode
npm test

# Run with coverage
npm run test:coverage
```

### End-to-End Tests

```bash
cd frontend-app

# Prerequisites:
# 1. Stop your development backend (port 8000)
# 2. Set OPENAI_API_KEY environment variable

# Run E2E tests
npm run test:e2e

# Run with UI mode
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Debug mode
npm run test:e2e:debug
```

**📖 For detailed E2E testing instructions, see [E2E_SETUP.md](frontend-app/E2E_SETUP.md)**

### Validation Query Dataset

The project includes a comprehensive validation dataset for testing AI-generated SQL queries:

**Location:** `backend/tests/fixtures/validation_queries.json`

This dataset contains 25 carefully crafted test cases with:
- Natural language questions
- Expected SQL queries
- Query categories (ranking, filtering, complex)
- Descriptions of what each test validates

**Categories:**
- **Ranking** (9 queries) - ORDER BY queries with LIMIT
- **Filtering** (11 queries) - WHERE clause conditions
- **Complex** (5 queries) - Multiple conditions, OR operators, pattern matching

#### Real Model Validation (Tests OpenAI API)

⚠️ **These tests use the REAL OpenAI API and cost money!**

```bash
cd backend

# Generate detailed validation report (recommended)
# ⚠️ This makes 25 API calls to OpenAI
python tests/validate_model.py

# Save report to file
python tests/validate_model.py --output validation_report.txt

# Run validation via pytest
pytest tests/test_validation_queries.py::TestRealModelValidation -v

# Run only dataset integrity tests (free, no API calls)
pytest tests/test_validation_queries.py::TestValidationDatasetIntegrity -v
```

**What Gets Tested:**
- ✅ AI generates syntactically valid SQL
- ✅ SQL contains expected clauses (WHERE, ORDER BY, LIMIT, LIKE, BETWEEN)
- ✅ SQL executes without errors
- ✅ Quality metrics and accuracy percentage by category

**Example Validation Entry:**
```json
{
  "id": 1,
  "question": "Show me the top 10 players by overall rating",
  "expected_sql": "SELECT * FROM players ORDER BY ovr DESC LIMIT 10",
  "category": "ranking",
  "description": "Basic ordering and limiting query"
}
```

**Validation Report Output:**
```
VALIDATION SUMMARY
==================
Total Queries: 25
Passed: 23 (92.0%)
Failed: 2 (8.0%)

Accuracy by Category:
  ranking     :  9/9 (100%)
  filtering   : 10/11 (91%)
  complex     :  4/5 (80%)
```

**Note:** The validation tests require:
- Valid `OPENAI_API_KEY` environment variable
- Will cost ~$0.05-0.10 per run (depending on model)
- Takes 2-5 minutes to complete all tests

## 📁 Project Structure

```
nlp-sql-interface/
├── backend/
│   ├── data/                    # Sample datasets
│   ├── models/                  # Request/Response models
│   ├── schemas/                 # Database schemas
│   ├── services/                # Business logic
│   │   ├── ai_service.py       # OpenAI integration
│   │   ├── auth_service.py     # Authentication
│   │   ├── query_service.py    # Query processing
│   │   ├── history_service.py  # Query history
│   │   └── ...
│   ├── tests/                   # Backend tests
│   │   ├── fixtures/            # Test data & validation queries
│   │   └── test_*.py            # Test files
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
│
├── frontend-app/
│   ├── e2e/                     # E2E tests (Playwright)
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── contexts/            # React contexts
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom hooks
│   │   ├── lib/                 # Utilities
│   │   └── integrations/        # API integration
│   ├── playwright.config.ts     # Playwright configuration
│   ├── vite.config.ts          # Vite configuration
│   └── package.json            # Node dependencies
│
├── .github/
│   └── workflows/
│       └── tests.yml           # CI/CD pipeline
│
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

**Backend (`backend/.env`):**
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_MODEL` - Model to use (default: `gpt-4o-mini`)

**Frontend:**
- Environment variables are passed through Vite and Playwright configurations

### Supported Models

- `gpt-4o-mini` (recommended, default)
- `gpt-4-turbo`
- `gpt-3.5-turbo`

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

1. **Backend Tests** - Runs pytest with coverage
2. **Frontend Tests** - Runs Vitest unit tests
3. **E2E Tests** - Runs Playwright tests with test database

All tests must pass before merging to `main` or `dev` branches.

**Required GitHub Secrets:**
- `OPENAI_API_KEY` - Your OpenAI API key

## 📊 Sample Queries

Try these example queries once the application is running:

- "Show me the top 10 players by overall rating"
- "List all players from Brazil with rating above 85"
- "Which players are strikers and have more than 80 pace?"
- "Show me the youngest players in the database"
- "Find players with high dribbling skills"

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Database Connection Issues
- Verify PostgreSQL is running
- Check credentials in `.env` file
- Ensure database exists: `createdb nlp_sql`

### OpenAI API Errors
- Verify API key is correct
- Check API rate limits and quotas
- Ensure `OPENAI_MODEL` is set to a supported model

### E2E Tests Failing
- Stop development backend before running E2E tests
- Ensure `OPENAI_API_KEY` is set in environment
- Verify test database exists: `createdb nlp_sql_test`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**Yossi Abu**

- GitHub: [@YossiAbu](https://github.com/YossiAbu)

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- LangChain for the SQL chain framework
- The FastAPI and React communities

---

**⚡ Built with FastAPI, React, and OpenAI**
