#!/bin/bash
set -e

# Write Firebase credentials from Environment Variable (if set)
if [ -n "$FIREBASE_CREDENTIALS_JSON" ]; then
    echo "Writing firebase_credentials.json from environment variable..."
    echo "$FIREBASE_CREDENTIALS_JSON" > /app/firebase_credentials.json
fi

# Run collectstatic to ensure static files are ready
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
# - workers=1: Only 1 worker to load heavy ML models ONCE (saves RAM)
# - threads=8: Process multiple requests concurrently within that worker
# - timeout=0: Disable Cloud Run timeout handling (let Cloud Run handle it)
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 smart_agriculture.wsgi:application
