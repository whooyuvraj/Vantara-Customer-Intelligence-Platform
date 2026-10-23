import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# Load serialized model and artifacts
model = joblib.load("models_artifacts/xgboost_churn_model.pkl")
feature_cols = joblib.load("models_artifacts/feature_cols.pkl")
kmeans = joblib.load("models_artifacts/kmeans_model.pkl")
seg_scaler = joblib.load("models_artifacts/segmentation_scaler.pkl")

# Initialize FastAPI application
app = FastAPI(
    title="Customer Behavior & Churn Prediction API",
    description="REST API for predicting customer churn risk and RFM segmentation",
    version="1.0.0"
)

# Request payload schema
class CustomerFeatures(BaseModel):
    Recency: float
    Frequency: float
    Monetary: float
    AvgBasketSize: float
    TotalOrders: float
    ReturnCount: float
    ReturnRate: float
    AvgOrderValue: float

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Customer Churn Prediction API",
        "version": "1.0.0"
    }

@app.post("/predict")
def predict_churn(customer: CustomerFeatures):
    # Convert incoming payload to DataFrame
    input_df = pd.DataFrame([customer.dict()])

    # Feature selection
    X = input_df[feature_cols]

    # Inference
    churn_prob = float(model.predict_proba(X)[0][1])
    churn_pred = int(churn_prob >= 0.5)

    # Segment identification
    seg_data = input_df[['Recency', 'Frequency', 'Monetary', 'AvgOrderValue']]
    seg_scaled = seg_scaler.transform(seg_data)
    cluster = int(kmeans.predict(seg_scaled)[0])

    # Risk level mapping
    if churn_prob >= 0.65:
        risk_level = "High"
    elif churn_prob >= 0.35:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "churn_prediction": churn_pred,
        "churn_probability": round(churn_prob, 4),
        "risk_level": risk_level,
        "assigned_cluster": cluster
    }
