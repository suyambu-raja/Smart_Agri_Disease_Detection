"""
Create Dummy Models for Testing
=================================
Generates a small CNN model (disease_model.h5) and a simple
sklearn model (yield_model.pkl) so the API endpoints work
end-to-end without needing real trained models.

Requirements:
  - Python 3.10 – 3.12
  - pip install tensorflow scikit-learn joblib numpy

Usage:
  python scripts/create_dummy_model.py
"""

import os
import sys
import numpy as np

# Ensure we save to the correct directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


def create_disease_model():
    """
    Create a lightweight CNN matching the expected input/output shape:
      Input:  (None, 224, 224, 3)
      Output: (None, 38)  — 38 PlantVillage classes
    """
    print("=" * 50)
    print("Creating Disease Detection CNN Model...")
    print("=" * 50)

    try:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers
    except ImportError:
        print("ERROR: TensorFlow is not installed.")
        print("Install it with: pip install tensorflow")
        print("NOTE: Requires Python 3.10–3.12")
        return False

    NUM_CLASSES = 38

    # Build a small MobileNetV2-based model (transfer learning)
    base_model = keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
    )
    base_model.trainable = False  # Freeze base layers

    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(NUM_CLASSES, activation='softmax'),
    ])

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy'],
    )

    model.summary()

    # Save the model (untrained — random weights on the dense layers)
    model_path = os.path.join(MODELS_DIR, 'disease_model.h5')
    model.save(model_path)
    print(f"\n✅ Disease model saved to: {model_path}")
    print(f"   File size: {os.path.getsize(model_path) / (1024*1024):.1f} MB")

    # Quick test
    dummy_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
    prediction = model.predict(dummy_input, verbose=0)
    print(f"   Test prediction shape: {prediction.shape}")
    print(f"   Test prediction sum:   {prediction[0].sum():.4f} (should be ~1.0)")

    return True


def create_yield_model():
    """
    Create a RandomForest regressor for yield prediction.
    Features: [district_enc, soil_enc, crop_enc, rainfall, temperature]
    Target:   predicted yield in kg/acre

    Trained on synthetic data to produce reasonable outputs.
    """
    print("\n" + "=" * 50)
    print("Creating Yield Prediction Model...")
    print("=" * 50)

    try:
        from sklearn.ensemble import RandomForestRegressor
        import joblib
    except ImportError:
        print("ERROR: scikit-learn is not installed.")
        print("Install it with: pip install scikit-learn joblib")
        return False

    np.random.seed(42)

    # Generate synthetic training data
    n_samples = 5000

    # Feature ranges (encoded values)
    district = np.random.randint(0, 18, n_samples)      # 18 districts
    soil_type = np.random.randint(0, 7, n_samples)       # 7 soil types
    crop = np.random.randint(0, 12, n_samples)            # 12 crops
    rainfall = np.random.uniform(30, 300, n_samples)      # mm
    temperature = np.random.uniform(15, 45, n_samples)    # °C

    X = np.column_stack([district, soil_type, crop, rainfall, temperature])

    # Generate realistic yield targets based on crop type
    base_yields = {
        0: 2800,   # Rice
        1: 2200,   # Wheat
        2: 3200,   # Maize
        3: 32000,  # Sugarcane
        4: 900,    # Cotton
        5: 1400,   # Groundnut
        6: 1100,   # Millets
        7: 900,    # Pulses
        8: 22000,  # Banana
        9: 5500,   # Coconut
        10: 2800,  # Turmeric
        11: 1600,  # Tea
    }

    y = np.zeros(n_samples)
    for i in range(n_samples):
        base = base_yields.get(int(crop[i]), 2000)

        # Rainfall effect (optimal around 100-150mm)
        rain_factor = 1.0 + 0.3 * np.sin((rainfall[i] - 50) / 100 * np.pi)
        rain_factor = max(0.4, min(rain_factor, 1.5))

        # Temperature effect (optimal around 25-30°C)
        temp_factor = 1.0 - 0.02 * abs(temperature[i] - 28)
        temp_factor = max(0.5, min(temp_factor, 1.2))

        # Soil suitability (add some variation)
        soil_factor = 0.85 + 0.15 * np.random.random()

        # District factor (slight regional variation)
        district_factor = 0.9 + 0.1 * np.random.random()

        y[i] = base * rain_factor * temp_factor * soil_factor * district_factor
        y[i] += np.random.normal(0, base * 0.05)  # Add noise
        y[i] = max(y[i], 50)  # Floor

    # Train the model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    # Evaluate
    train_score = model.score(X, y)
    print(f"   Training R² score: {train_score:.4f}")

    # Save
    model_path = os.path.join(MODELS_DIR, 'yield_model.pkl')
    joblib.dump(model, model_path)
    print(f"\n✅ Yield model saved to: {model_path}")
    print(f"   File size: {os.path.getsize(model_path) / (1024*1024):.1f} MB")

    # Quick test
    test_input = np.array([[0, 0, 0, 120, 30]])  # Coimbatore, Black Soil, Rice
    test_pred = model.predict(test_input)
    print(f"   Test prediction (Rice, Coimbatore): {test_pred[0]:.0f} kg/acre")

    return True


if __name__ == '__main__':
    print("🌱 Smart Agriculture – Model Generator")
    print("=" * 50)

    disease_ok = create_disease_model()
    yield_ok = create_yield_model()

    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Disease Model (CNN):        {'✅ Created' if disease_ok else '❌ Failed'}")
    print(f"  Yield Model (RandomForest): {'✅ Created' if yield_ok else '❌ Failed'}")
    print("=" * 50)

    if not disease_ok:
        print("\n⚠️  Disease model requires TensorFlow (Python 3.10-3.12).")
        print("   The server will run in MOCK mode until the model is available.")
