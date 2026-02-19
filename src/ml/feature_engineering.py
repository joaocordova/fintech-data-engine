import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def get_training_data(ticker="AAPL", years=2):
    """
    Fetches REAL historical data using yfinance.
    Simulates Sentiment for the demo (since we lack a Reddit Archive API key).
    """
    print(f"Fetching real market data for {ticker}...")
    
    # 1. Fetch Real Price Data
    start_date = (datetime.today() - timedelta(days=years*365)).strftime('%Y-%m-%d')
    df_yahoo = yf.download(ticker, start=start_date, progress=False)
    
    # Reset index to get 'Date' as a column
    df_yahoo = df_yahoo.reset_index()
    
    # Prepare Prophet Schema (ds, y)
    # yfinance columns might be MultiIndex/Tuple depending on version. 
    # Flattening logic:
    if isinstance(df_yahoo.columns, pd.MultiIndex):
        df_yahoo.columns = df_yahoo.columns.get_level_values(0)
    
    # Rename columns for Prophet
    # Date -> ds, Close -> y
    # Note: Column names are usually 'Date' and 'Close' (capitalized)
    df = df_yahoo[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
    
    # 2. Simulate Sentiment (Synethic for now)
    # in a real app, this would be a JOIN with the 'fact_sentiment' table
    n_rows = len(df)
    print(f"Downloaded {n_rows} days of data.")
    
    sentiment = np.random.normal(0, 0.2, n_rows).cumsum()
    sentiment = np.clip(sentiment, -1, 1) # Bound between -1 and 1
    
    df['sentiment'] = sentiment
    df['symbol'] = ticker
    
    # Feature Engineering: Lagged Sentiment
    df['sentiment_lag_1'] = df['sentiment'].shift(1).fillna(0)
    
    return df

if __name__ == "__main__":
    df = get_training_data("NVDA") # Example: Nvidia
    print(df.tail())
    df.to_csv("src/ml/training_data.csv", index=False)
