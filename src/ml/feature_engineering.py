import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_training_data(days=365):
    """
    Simulates reading from the 'Gold' layer (Postgres).
    Generates synthetic data for:
    - Apple (AAPL) Stock Price
    - Reddit Sentiment Score (-1 to 1)
    """
    dates = pd.date_range(end=datetime.today(), periods=days, freq='D')
    
    # Simulate Sentiment (Random Walk with momentum)
    sentiment = np.random.normal(0, 0.2, days).cumsum()
    sentiment = np.clip(sentiment, -1, 1) # Bound between -1 and 1
    
    # Simulate Stock Price influenced by Sentiment
    # Price follows random walk + sentiment impact
    price = 150.0 + np.random.normal(0, 2, days).cumsum() + (sentiment * 5)
    
    df = pd.DataFrame({
        'ds': dates,
        'y': price,
        'sentiment': sentiment,
        'symbol': 'AAPL'
    })
    
    # Feature Engineering: Lagged Sentiment
    # "Yesterday's sentiment affects today's price"
    df['sentiment_lag_1'] = df['sentiment'].shift(1).fillna(0)
    
    return df

if __name__ == "__main__":
    df = get_training_data()
    print(df.tail())
    df.to_csv("src/ml/training_data.csv", index=False)
