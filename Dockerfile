FROM python:3.11-slim

WORKDIR /code

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    --no-install-recommends

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the entire project including alembic configuration
COPY . /code/

# Create necessary directories
RUN mkdir -p /code/app/static/budgets /code/temp /code/static /code/templates/pdf

# Make the startup script executable
RUN chmod +x /code/start.sh

# Expose port 8080
EXPOSE 8080

CMD ["./start.sh"]