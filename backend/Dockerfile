# Production image for Render. Build context: backend/
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN useradd --create-home hajz
USER hajz

ENV PORT=8000
EXPOSE 8000

# Apply pending migrations and the idempotent reference seeders, then serve. Render sets PORT.
CMD ["sh", "-c", "python manage.py migrate && python manage.py seed && exec gunicorn 'app:create_app()' --bind 0.0.0.0:${PORT} --workers 2 --timeout 60 --access-logfile -"]
