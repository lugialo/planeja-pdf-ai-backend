FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    curl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the entire project
COPY . /code/

# Create necessary directories
RUN mkdir -p /code/app/static/budgets \
             /code/temp \
             /code/static \
             /code/templates/pdf

# Make startup script executable
RUN chmod +x /code/start.sh

# Verify project structure
RUN ls -la /code/ && \
    ls -la /code/app/ && \
    ls -la /code/alembic/ && \
    echo "✅ Project structure verified"

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["./start.sh"]