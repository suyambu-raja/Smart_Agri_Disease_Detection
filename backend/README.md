# Smart Agriculture – Crop Disease & Yield Prediction System

A production-ready Django REST Framework backend for agricultural disease detection, yield prediction, and treatment recommendations.

## 🏗️ Tech Stack

| Component            | Technology                     |
|----------------------|-------------------------------|
| Backend Framework    | Django + Django REST Framework |
| Database             | Firebase Firestore             |
| Authentication       | Firebase Auth (ID tokens)      |
| Disease Detection    | TensorFlow/Keras CNN           |
| Yield Prediction     | Scikit-learn                   |
| Recommendations      | Rule-based Expert System       |
| Static Files         | WhiteNoise                     |
| Configuration        | python-dotenv                  |

## 📁 Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── .env                        # Environment variables (DO NOT commit)
├── .env.example                # Template for team members
├── firebase_credentials.json   # Firebase service account (DO NOT commit)
├── smart_agriculture/          # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── firebase_init.py        # Firebase singleton initializer
│   ├── firebase_auth.py        # DRF custom authentication
│   ├── exceptions.py           # Custom error handler
│   ├── wsgi.py
│   └── asgi.py
├── users/                      # User profile management
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── disease/                    # Disease detection API
│   ├── ml_model.py             # CNN model loader (singleton)
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── yield_prediction/           # Yield prediction API
│   ├── ml_model.py             # sklearn model loader (singleton)
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── recommendation/             # Treatment recommendations
│   ├── knowledge_base.py       # Expert rules for 38 diseases
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── models/                     # ML model files
    ├── disease_model.h5        # CNN weights (add yours)
    └── yield_model.pkl         # sklearn pipeline (add yours)
```

## 🚀 Quick Start

### 1. Clone & Setup Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: TensorFlow requires Python 3.10–3.12. If you're on 3.13+, the disease endpoint will run in mock mode.

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Place ML Models

Copy your trained models to the `models/` directory:
- `models/disease_model.h5`  (Keras CNN)
- `models/yield_model.pkl`   (sklearn pipeline)

### 5. Run Migrations & Start Server

```bash
python manage.py migrate
python manage.py runserver
```

Server will be running at `http://127.0.0.1:8000/`

## 📡 API Endpoints

### Health Check
```
GET /
GET /health/
```

### Disease Detection
```
POST /api/disease/predict/
Content-Type: multipart/form-data
Authorization: Bearer <firebase_id_token>

Body: image=<file>

Response:
{
  "success": true,
  "disease_name": "Tomato Early Blight",
  "confidence": 92.45,
  "is_healthy": false
}
```

### Yield Prediction
```
POST /api/yield/predict/
Content-Type: application/json
Authorization: Bearer <firebase_id_token>

Body:
{
  "district": "Coimbatore",
  "soil_type": "Black Soil",
  "crop": "Rice",
  "rainfall": 120,
  "temperature": 30
}

Response:
{
  "success": true,
  "predicted_yield": 3450,
  "unit": "kg/acre",
  "risk_level": "Low"
}
```

### Recommendations
```
GET /api/recommendation/?disease_name=Tomato+Early+Blight
Authorization: Bearer <firebase_id_token>

Response:
{
  "success": true,
  "disease_name": "Tomato Early Blight",
  "fertilizers": [...],
  "pesticides": [...],
  "organic_treatments": [...],
  "preventive_measures": [...]
}
```

### List Available Diseases
```
GET /api/recommendation/diseases/
Authorization: Bearer <firebase_id_token>
```

### User Profile
```
GET  /api/users/profile/     → Get profile
POST /api/users/profile/     → Create/update profile

Authorization: Bearer <firebase_id_token>
```

### Prediction History
```
GET /api/disease/history/
GET /api/yield/history/

Authorization: Bearer <firebase_id_token>
```

## 🔐 Authentication

All endpoints (except `/`, `/health/`, and `/api/users/health/`) require a **Firebase ID token** in the `Authorization` header:

```
Authorization: Bearer <firebase_id_token>
```

The backend verifies the token using Firebase Admin SDK.

## 🚢 Deploy to Render

### 1. Create `render.yaml`

```yaml
services:
  - type: web
    name: smart-agriculture-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    startCommand: gunicorn smart_agriculture.wsgi:application --bind 0.0.0.0:$PORT
    envVars:
      - key: DJANGO_SECRET_KEY
        generateValue: true
      - key: DJANGO_DEBUG
        value: "False"
      - key: DJANGO_ALLOWED_HOSTS
        value: ".onrender.com"
      - key: FIREBASE_CREDENTIALS_PATH
        value: firebase_credentials.json
```

### 2. Push to GitHub & Connect Render

1. Push your code to GitHub (ensure `.gitignore` excludes `.env` and credentials)
2. Go to [render.com](https://render.com)
3. Create a new **Web Service** → connect your repo
4. Use **Python 3.12** runtime
5. Set environment variables in Render's dashboard
6. Upload `firebase_credentials.json` via Render's secret files

### 3. Upload ML Models

For Render's free tier, models must be within the repo or fetched at build time. Consider:
- Adding a build script to download models from Google Drive / S3
- Using Git LFS for model files

## 📝 License

MIT
