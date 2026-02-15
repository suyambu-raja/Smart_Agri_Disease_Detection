#!/bin/bash
set -e

# Write Firebase credentials from Environment Variable (if set)
# Use Python to handle newlines correctly and avoid shell escaping issues
if [ -n "$FIREBASE_CREDENTIALS_JSON" ]; then
    echo "Found FIREBASE_CREDENTIALS_JSON env var. Writing to file..."
    python -c "import os; open('/app/firebase_credentials.json', 'w').write(os.environ.get('FIREBASE_CREDENTIALS_JSON', ''))"
else
    echo "WARNING: FIREBASE_CREDENTIALS_JSON environment variable is NOT set!"
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
