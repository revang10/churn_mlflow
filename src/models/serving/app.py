import mlflow
import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# =====================
# FASTAPI APP
# =====================

app = FastAPI(title="Churn Prediction API")

# =====================
# LOAD PRODUCTION MODEL
# =====================

MODEL_NAME = "churn_model"
MODEL_STAGE = "production"

model_uri = f"models:/{MODEL_NAME}@{MODEL_STAGE}"

model = mlflow.sklearn.load_model(model_uri)

# =====================
# INPUT SCHEMA
# =====================

class CustomerFeatures(BaseModel):
    order_last_30_days: int
    avg_delivery_time: float
    late_delivery_ratio: float
    avg_order_value: float
    support_tickets_last_30_days: int
    days_since_last_order: int

# =====================
# HEALTH CHECK             

@app.get("/")
def health_check():
    return {"status": "API is running"}

# =====================
# PREDICTION ENDPOINT
# =====================

@app.post("/predict")
def predict_churn(features: CustomerFeatures):

    data = pd.DataFrame([{
        "order_las_30_days": features.order_last_30_days,
        "avg_delivery_time": features.avg_delivery_time,
        "late_delivery_ratio": features.late_delivery_ratio,
        "avg_order_value": features.avg_order_value,
        "support_tickets_last_30_days": features.support_tickets_last_30_days,
        "days_since_last_order": features.days_since_last_order
    }])
  
    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0][1]

    return {
        "churn_prediction": int(prediction),
        "churn_probability": round(float(probability), 3)
    }
