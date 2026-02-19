from fastapi import FastAPI, HTTPException
import mlflow.prophet
import pandas as pd
from datetime import datetime, timedelta
from pydantic import BaseModel

app = FastAPI()

# Input Schema
class PredictionRequest(BaseModel):
    sentiment_score: float # Current sentiment (-1 to 1)

# Load Model (Global for simplicity, use Model Registry in Prod)
MODEL_URI = "models:/AAPL_Volatility_Forecast/Production" # Hypothetical URI
# In this demo, we'll look for the latest run in mlruns or fail gracefully
try:
    # Need to identify run_id dynamically or use a fixed path for demo
    # For now, we will mock the prediction if no model is found
    model = None 
except:
    model = None

@app.post("/predict")
def predict(request: PredictionRequest):
    """
    Predicts next 7 days price based on today's sentiment.
    """
    # Create future dataframe
    dates = pd.date_range(start=datetime.today(), periods=7, freq='D')
    future = pd.DataFrame({'ds': dates})
    
    # Simple logic: Assume sentiment decays over 7 days
    future['sentiment_lag_1'] = [request.sentiment_score * (0.9**i) for i in range(7)]
    
    # Mock Prediction if model not loaded
    if model is None:
        # Logistic growth simulation
        base_price = 150.0
        preds = [base_price * (1 + request.sentiment_score * 0.01 * i) for i in range(7)]
    else:
        forecast = model.predict(future)
        preds = forecast['yhat'].values.tolist()
        
    return {
        "symbol": "AAPL",
        "forecast_dates": [d.strftime('%Y-%m-%d') for d in dates],
        "predicted_prices": preds
    }
