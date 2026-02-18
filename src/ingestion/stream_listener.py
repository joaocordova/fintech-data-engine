from fastapi import FastAPI, WebSocket
import asyncio
import json
import pandas as pd
from datetime import datetime
import os

app = FastAPI()

# Buffer for micro-batching
BUFFER = []
BATCH_SIZE = 100
FLUSH_INTERVAL = 5 # seconds

async def flush_buffer():
    """
    Writes in-memory buffer to ADLS (Simulated) as a JSON/Parquet file.
    This runs periodically to prevent data loss.
    """
    global BUFFER
    while True:
        await asyncio.sleep(FLUSH_INTERVAL)
        if BUFFER:
            # Atomic micro-batch write
            chunk = BUFFER[:]
            BUFFER = []
            
            df = pd.DataFrame(chunk)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"streaming/market/batch_{timestamp}.json"
            
            # Simulate ADLS Write
            local_path = f"raw_data/{filename}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            df.to_json(local_path, orient="records")
            print(f"Flushed {len(chunk)} records to {local_path}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(flush_buffer())

@app.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
    """
    Simulated WebSocket endpoint that receives market data.
    In prod, this might connect TO Alpaca. 
    Here, it ACTS as a receiver or a proxy.
    """
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            record = json.loads(data)
            
            # Add metadata
            record["ingestion_time"] = datetime.now().isoformat()
            
            # Add to buffer
            BUFFER.append(record)
            
            if len(BUFFER) >= BATCH_SIZE:
                 # Trigger immediate flush if buffer full (logic simplified)
                 pass
                 
        except Exception as e:
            print(f"Error: {e}")
            break
