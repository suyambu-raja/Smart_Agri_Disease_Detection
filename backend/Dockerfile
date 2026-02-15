# Use official lightweight Python image (Python 3.11 is stable for TensorFlow)
FROM python:3.11-slim

# Set environment variables
# - PYTHONDONTWRITEBYTECODE: Stops Python from generating .pyc files
# - PYTHONUNBUFFERED: Forces stdin/stdout/stderr to be unbuffered (logs show up immediately)
# - PORT: Default port for Cloud Run
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
# - gcc, libpq-dev: For building Python packages (like psycopg2) if wheels are missing
# - libgl1: Required if using OpenCV (cv2) for image processing
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Run collectstatic to serve static files (CSS/JS) via WhiteNoise
RUN python manage.py collectstatic --noinput

# Expose the port
EXPOSE 8080

# Run gunicorn
# - workers=1: Only 1 worker to load heavy ML models ONCE (saves RAM)
# - threads=8: Process multiple requests concurrently within that worker
# - timeout=0: Disable Cloud Run timeout handling (let Cloud Run handle it)
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 smart_agriculture.wsgi:application
