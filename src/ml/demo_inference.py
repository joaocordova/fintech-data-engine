import pandas as pd
import mlflow.prophet
import os
from datetime import datetime, timedelta

def run_demo():
    print("--- ML Inference Demo ---")
    
    # 1. Find the latest MLflow run
    try:
        run_id = mlflow.search_runs(experiment_names=["AAPL_Volatility_Forecast"]) \
            .iloc[0]['run_id']
        print(f"Loading model from Run ID: {run_id}")
        
        logged_model = f"runs:/{run_id}/model"
        model = mlflow.prophet.load_model(logged_model)
    except Exception as e:
        print(f"Could not load model: {e}")
        print("Falling back to rule-based logic for demo.")
        model = None

    # 2. Define Scenarios
    scenarios = [
        {"sentiment": 0.9, "label": "Highly Positive (Reddit loves it)"},
        {"sentiment": -0.8, "label": "Highly Negative (FUD / Crash fears)"}
    ]
    
    dates = pd.date_range(start=datetime.today() + timedelta(days=1), periods=7, freq='D')
    
    for s in scenarios:
        print(f"\nScenario: {s['label']} (Score: {s['sentiment']})")
        
        future = pd.DataFrame({'ds': dates})
        # Simulate decaying impact of today's news
        future['sentiment_lag_1'] = [s['sentiment'] * (0.8**i) for i in range(7)]
        
        if model:
            forecast = model.predict(future)
            preds = forecast['yhat'].values
        else:
            # Fallback mock
            base = 180
            preds = [base * (1 + s['sentiment']*0.01*i) for i in range(7)]
            
        print("Forecast next 7 days:")
        for d, p in zip(dates, preds):
            print(f"  {d.strftime('%Y-%m-%d')}: ${p:.2f}")

if __name__ == "__main__":
    run_demo()
