FROM python:3.12-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install  -r requirements.txt

# Copy project files
COPY . .

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && uvicorn backend.asgi:application --host 0.0.0.0 --port 8000"]