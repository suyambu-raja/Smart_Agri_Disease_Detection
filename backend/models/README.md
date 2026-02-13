# ML Models Directory

Place your pre-trained models here:

1. **disease_model.h5** – TensorFlow/Keras CNN model trained on PlantVillage dataset
2. **yield_model.pkl** – Scikit-learn model (Random Forest / XGBoost) for yield prediction

## Notes
- These files are excluded from git via .gitignore (they are too large).
- If models are not present, the server will start in **mock mode** 
  and return sample predictions for development/testing.
- Upload your trained models to this directory before deploying to production.
