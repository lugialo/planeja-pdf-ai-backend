#!/bin/bash

set -e

echo "🚀 Starting planeja-pdf-ai-backend..."

# Set working directory to /code (where our app is)
cd /code

# Show current environment
echo "📍 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "🔧 Environment: ${ENVIRONMENT:-production}"

# List important files to verify they exist
echo "📁 Checking project structure:"
ls -la app/ || echo "❌ app/ directory not found"
ls -la alembic/ || echo "❌ alembic/ directory not found"
ls -la alembic.ini || echo "❌ alembic.ini not found"

# Check if alembic is installed and available
echo "🔍 Checking alembic installation:"
which alembic && alembic --version || echo "❌ Alembic not available"

# Try to run database migrations
echo "🗄️ Running database migrations..."
if alembic upgrade head 2>&1; then
    echo "✅ Database migrations completed successfully"
else
    echo "⚠️ Migration failed or DB already up-to-date, continuing..."
fi

# Show final migration status
echo "📊 Current migration status:"
alembic current 2>&1 || echo "Could not determine migration status"

# Start the FastAPI application
echo "🌐 Starting FastAPI application on port 8080..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker --timeout 200 --bind 0.0.0.0:8080 app.main:app

