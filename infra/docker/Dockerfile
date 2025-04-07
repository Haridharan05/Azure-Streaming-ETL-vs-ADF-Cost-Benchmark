# Multi‑stage build for slim image

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src /app/src

# Gunicorn entrypoint
ENV GUNICORN_CMD_ARGS="--workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 0"
CMD ["gunicorn", "src.app.main:app"]