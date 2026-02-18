import os
import pandas as pd
from datetime import date, timedelta
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
import pandera as pa

# Mocking Alpaca API for demonstration if no key provided
try:
    from alpaca_trade_api.rest import REST, TimeFrame
except ImportError:
    pass

# Contract Definition (Senior Level: Validate at edge)
schema = pa.DataFrameSchema({
    "symbol": pa.Column(str),
    "timestamp": pa.Column(pa.DateTime),
    "open": pa.Column(float, checks=pa.Check.ge(0)),
    "high": pa.Column(float, checks=pa.Check.ge(0)),
    "low": pa.Column(float, checks=pa.Check.ge(0)),
    "close": pa.Column(float, checks=pa.Check.ge(0)),
    "volume": pa.Column(int, checks=pa.Check.ge(0)),
})

def get_historical_data(symbol: str, start_date: str, end_date: str):
    """
    Fetches historical data. In a real scenario, calls Alpaca REST API.
    Here we generate mock data for portability of the demo.
    """
    print(f"Fetching history for {symbol} from {start_date} to {end_date}...")
    # Mock data generation
    dates = pd.date_range(start=start_date, end=end_date, freq="1min")
    df = pd.DataFrame({
        "symbol": symbol,
        "timestamp": dates,
        "open": 100.0,
        "high": 105.0,
        "low": 95.0,
        "close": 102.0,
        "volume": 1000
    })
    return df

def upload_to_adls(df: pd.DataFrame, file_system: str, path: str):
    """
    Uploads DataFrame to ADLS Gen 2 as Parquet.
    Uses DefaultAzureCredential for security (Managed Identity).
    """
    try:
        # In a real run, we would use proper credentials
        # service_client = DataLakeServiceClient(account_url="https://<account>.dfs.core.windows.net", credential=DefaultAzureCredential())
        # file_system_client = service_client.get_file_system_client(file_system)
        # file_client = file_system_client.get_file_client(path)
        
        # Simulating upload by saving locally for this demo
        local_path = f"raw_data/{path}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        df.to_parquet(local_path)
        print(f"Uploaded {len(df)} rows to {local_path} (Simulated ADLS)")
    except Exception as e:
        print(f"Failed to upload: {e}")

def run_batch_job(execution_date: str):
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    # Idempotency: Overwrite the partition for this specific date
    # Folder structure: bronze/market/date=YYYY-MM-DD/file.parquet
    
    for symbol in symbols:
        df = get_historical_data(symbol, execution_date, execution_date)
        
        # Enforce Contract
        try:
            validated_df = schema.validate(df)
            
            # Write to Bronze
            path = f"market/date={execution_date}/{symbol}.parquet"
            upload_to_adls(validated_df, "bronze", path)
            
        except pa.errors.SchemaError as e:
            print(f"CONTRACT VIOLATION for {symbol}: {e}")
            # Logic to send to Dead Letter Queue (DLQ)

if __name__ == "__main__":
    # Simulate running for yesterday
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    run_batch_job(yesterday)
