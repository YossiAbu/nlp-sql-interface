#!/bin/bash
set -e

echo "⏳ Waiting for database to be ready..."
sleep 2

echo "📊 Loading player data into database..."
python load_data.py || echo "⚠️ Data already loaded or error occurred"

echo "🚀 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload