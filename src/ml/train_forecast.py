import pandas as pd
from prophet import Prophet
import mlflow
import mlflow.prophet
from sklearn.metrics import mean_absolute_error
from feature_engineering import get_training_data
import os

def train_forecast_model():
    # 1. Load Data
    df = get_training_data(days=365)
    
    # Split Train/Test
    train_size = int(len(df) * 0.9)
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]
    
    # 2. Setup MLflow
    mlflow.set_experiment("AAPL_Volatility_Forecast")
    
    with mlflow.start_run():
        # 3. Define Prophet Model
        # We add 'sentiment_lag_1' to see if it helps prediction
        model = Prophet(daily_seasonality=True, yearly_seasonality=True)
        model.add_regressor('sentiment_lag_1')
        
        # 4. Train
        model.fit(train_df)
        
        # 5. Evaluate
        future = test_df[['ds', 'sentiment_lag_1']]
        forecast = model.predict(future)
        
        # Calculate Metrics
        mae = mean_absolute_error(test_df['y'], forecast['yhat'])
        print(f"Mean Absolute Error: {mae:.2f}")
        
        # 6. Log to MLflow
        mlflow.log_metric("mae", mae)
        mlflow.log_param("model_type", "Prophet")
        mlflow.log_param("regressor", "Sentiment")
        
        # Save Model
        mlflow.prophet.log_model(model, "model")
        
        return model, forecast

if __name__ == "__main__":
    # Ensure mlruns directory exists
    os.makedirs("mlruns", exist_ok=True)
    train_forecast_model()
