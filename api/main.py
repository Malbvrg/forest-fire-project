from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd

from src.models import model_dur, model_area

app = FastAPI(title="Fire Forecast API")

feature_cols = [
    "month",
    "day_of_year",
    "temp_3d_lag",
    "wind_3d_max_lag",
    "rain_7d_sum_lag",
]

class FireInput(BaseModel):
    month: int
    day_of_year: int
    temp_3d_lag: float
    wind_3d_max_lag: float
    rain_7d_sum_lag: float

class FireOutput(BaseModel):
    pred_duration_days: float
    pred_area_ha: float          # число (может быть 0)
    area_is_small: bool           # новый флаг: True, если площадь < 1 га

@app.post("/predict", response_model=FireOutput)
def predict(input_data: FireInput):
    df = pd.DataFrame([input_data.dict()])
    X = df[feature_cols]

    pred_dur = float(model_dur.predict(X)[0])

    # Прогноз площади
    pred_area_log = model_area.predict(X)[0]
    pred_area = float(np.expm1(pred_area_log))

    # Защита от отрицательных значений
    pred_area = max(0.0, pred_area)

    # Флаг: если площадь меньше 1 га — помечаем
    area_is_small = pred_area < 1.0

    return FireOutput(
        pred_duration_days=pred_dur,
        pred_area_ha=pred_area,
        area_is_small=area_is_small
    )

@app.get("/")
def root():
    return {"message": "Fire Forecast API is running."}
