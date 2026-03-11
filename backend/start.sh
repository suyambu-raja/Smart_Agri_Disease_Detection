#!/bin/bash
# DO NOT use set -e — we want to see all errors, not crash silently

echo "========================================"
echo " Smart Agri Backend – Starting Up"
echo "========================================"
echo "PORT=$PORT"
echo "Working directory: $(pwd)"
echo "Python: $(python --version 2>&1)"

# Step 1: Firebase credentials
echo "[1/4] Firebase credentials..."
if [ -n "$FIREBASE_CREDENTIALS_JSON" ]; then
    python -c "import os; open('/app/firebase_credentials.json', 'w').write(os.environ.get('FIREBASE_CREDENTIALS_JSON', ''))" 2>&1 || true
    echo "  Written."
else
    echo "  WARNING: FIREBASE_CREDENTIALS_JSON not set (skipping)"
fi

# Step 2: collectstatic — skip if it takes too long
echo "[2/4] Collecting static files..."
timeout 30 python manage.py collectstatic --noinput 2>&1 || echo "  collectstatic skipped or had errors (non-fatal)"

# Step 3: migrate
echo "[3/4] Running migrations..."
timeout 30 python manage.py migrate --noinput 2>&1 || echo "  migrate skipped or had errors (non-fatal)"

# Step 4: Start Gunicorn
echo "[4/4] Starting Gunicorn on 0.0.0.0:$PORT ..."
echo "========================================"
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 smart_agriculture.wsgi:application
