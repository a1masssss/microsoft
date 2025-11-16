FROM python:3.12-slim

WORKDIR /app

# Copy requirements from root
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend directory
COPY backend/ .

# Note: frontend/dist will be mounted via volume at runtime
# Collect static files (ignore errors if frontend not built yet)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run migrations and start ASGI server
CMD ["sh", "-c", "python manage.py migrate && uvicorn backend.asgi:application --host 0.0.0.0 --port 8000"]