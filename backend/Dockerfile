# Use official lightweight Python image (Python 3.11 is stable for TensorFlow)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Django settings for production
ENV DJANGO_SECRET_KEY=hf-space-auto-generated-secret-key-2026
ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com,.hf.space,suyambu08-smart-agri-backend.hf.space

# Firebase
ENV FIREBASE_CREDENTIALS_PATH=firebase_credentials.json

# CORS – allow frontend origins
ENV CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://smart-agri-disease-detection.vercel.app,https://smart-agri-disease-detection.netlify.app

# Note: API keys should be set via Hugging Face Spaces Settings > Repository secrets

# Set work directory
WORKDIR /app

# Install system dependencies
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

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose the port
EXPOSE 8080

# Use startup script
CMD ["/app/start.sh"]
