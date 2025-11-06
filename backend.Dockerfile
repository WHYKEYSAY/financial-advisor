FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for Tesseract OCR and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-chi-sim \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY _monorepo/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY _monorepo/backend/app ./app
COPY _monorepo/backend/alembic ./alembic
COPY _monorepo/backend/alembic.ini .
COPY _monorepo/backend/scripts ./scripts

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Railway will override this with startCommand from railway.toml
# Default for local development
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
