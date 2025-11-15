FROM python:3.12-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run migrations and start ASGI server
CMD ["sh", "-c", "python manage.py migrate && uvicorn backend.asgi:application --host 0.0.0.0 --port 8000"]