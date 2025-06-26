#!/bin/bash

set -e

echo "Starting application..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 app.main:app
