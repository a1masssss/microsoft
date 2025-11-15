# Use Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for dataset if it doesn't exist
RUN mkdir -p /app/backend/mcp/dataset

# Expose port
EXPOSE 8000

# Default command (will be overridden by docker-compose)
CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]

