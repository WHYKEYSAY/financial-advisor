#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding credit cards data..."
python scripts/seed_credit_cards_extended.py || echo "Seed script failed or already seeded"

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
