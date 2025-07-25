#!/bin/bash
set -e

# Run migrations by default (can be disabled with RUN_MIGRATIONS=false)
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "🔄 Running database migrations..."
    alembic upgrade head
    echo "✅ Migrations completed!"
else
    echo "⏭️ Skipping database migrations (RUN_MIGRATIONS=false)"
fi

echo "🚀 Starting application..."
exec uvicorn src.presentation.main:app --host 0.0.0.0 --port 8000 