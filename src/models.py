import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(os.path.dirname(BASE_DIR), "models")

model_dur = joblib.load(os.path.join(MODELS_DIR, "duration_model.pkl"))
model_area = joblib.load(os.path.join(MODELS_DIR, "area_model.pkl"))
