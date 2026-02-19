# Phase 7: Machine Learning (Time Series Forecasting)

## 1. Architectural Decisions

| Decision | Choice | Alternative | Reasoning ("Senior" Level) |
| :--- | :--- | :--- | :--- |
| **Model** | **Prophet** (Meta) | LSTM / ARIMA | Prophet handles **missing data**, **holidays**, and **seasonality** out-of-the-box better than ARIMA. It is far more interpretable and faster to train than Deep Learning (LSTM) for this scale of data. |
| **Feature** | **Sentiment as Regressor** | Price Only | We hypothesize that social sentiment (Reddit) leads price action. Adding it as an "External Regressor" allows the model to learn this correlation. |
| **Tracking** | **MLflow** | Print Statements | In a team, you need to track *which* parameters produced the best model. MLflow provides a persistent record of experiments. |

## 2. Implementation Steps

### Step 1: Feature Engineering (`src/ml/feature_engineering.py`)
We simulate correct "Gold Layer" data extraction.
*   **Technique**: Lag Feature (`sentiment_lag_1`).
*   **Why**: We can't use *today's* sentiment to predict *today's* closing price at the start of the day. We must use *yesterday's* sentiment to predict *today's* price.

### Step 2: Training Pipeline (`src/ml/train_forecast.py`)
We automate the training loop.
1.  Splits data into Train (First 90%) and Test (Last 10%) to measure "Out of Sample" accuracy.
2.  Initializes Prophet and adds the `sentiment` regressor.
3.  Fits the model.
4.  Logs the **MAE (Mean Absolute Error)** to MLflow.

## 3. How to Run

1.  **Install dependencies**:
    ```bash
    pip install prophet mlflow scikit-learn
    ```

2.  **Run Training**:
    ```bash
    python src/ml/train_forecast.py
    ```

3.  **View Experiments**:
    ```bash
    mlflow ui
    # Open http://localhost:5000 to see your run metrics
    ```
