# Smart Agriculture AI 🌱

Cutting-edge disease detection, yield prediction, and treatment recommendation system powered by AI.

## Quick Start (For Friends) 🚀

Instead of pushing huge `node_modules` folders (which break things), just run this:

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/suyambu-raja/Smart_Agri_Disease_Detection.git
    cd Smart_Agri_Disease_Detection
    ```

2.  **Run the Setup Script** (Windows):
    Double-click `setup_project.bat` to install everything automatically!

    **OR manually:**

    **Backend:**
    ```bash
    cd backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```

    **Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## Features ✨
- **Disease Detection**: Upload leaf images (Tomato, Potato, etc.) to detect diseases instantly using MobileNetV2.
- **Yield Prediction**: Predict crop yield based on soil, rainfall, and temperature using Random Forest.
- **Treatment Guide**: Get organic and chemical treatment plans.
- **History Tracking**: Keep a log of all your detections.

## Tech Stack 🛠️
- **Frontend**: React, Vite, TypeScript, TailwindCSS
- **Backend**: Django REST Framework, Python
- **AI Models**: TensorFlow (Keras), Scikit-Learn
- **Database**: Django SQLite (History), Firebase (Auth)

## Dataset 📊
Includes ~50,000 images from the **PlantVillage** dataset covering 14 crops.
