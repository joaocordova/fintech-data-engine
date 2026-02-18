# Data Quality Framework & Contracts

## 1. Data Contracts (Ingestion Layer)
**Goal**: Prevent "Garbage In" by validating data *before* it enters the Bronze layer.
**Tool**: `Pandera` (Python) for runtime validation during ingestion.

### Contract Definition (Example)
We define a strict schema for the market data stream. If the API response violates this, the ingestion job **fails fast** or quarantines the record, rather than polluting the lake.

```python
import pandera as pa
from pandera.typing import DataFrame, Series

class MarketTrade(pa.SchemaModel):
    symbol: Series[str] = pa.Field(str_matches=r'^[A-Z]+$') # Uppercase only
    price: Series[float] = pa.Field(ge=0) # Price must be positive
    timestamp: Series[pa.DateTime]
    volume: Series[int] = pa.Field(ge=0)
    
    class Config:
        strict = True # No unknown columns allowed
```

### Handling Violations
*   **Blocking**: In Batch mode, if >1% of rows fail, abort the load.
*   **Quarantine**: In Streaming mode, bad records are sent to a "Dead Letter Queue" (DLQ) in ADLS `_quarantine/` folder for manual inspection.

## 2. Data Quality Checks (Transformation Layer)
**Goal**: Ensure business logic correctness and data freshness.
**Tool**: `Soda Core` (integrated with Airflow and dbt).

### Quality Checks (Silver/Gold)
We run these checks *after* every dbt model build.

| Check Type | Description | Target / Threshold |
| :--- | :--- | :--- |
| **Freshness** | Ensure data is arriving on time. | `MAX(timestamp) > NOW() - 5 minutes` (for Real-time) |
| **Volume** | Ensure we aren't losing data. | `ROW_COUNT > 0` and `ROW_COUNT > Yesterday * 0.9` |
| **Referential Integrity** | Ensure foreign keys match. | `trades.symbol` must exist in `dim_symbol.symbol` |
| **Schema** | Ensure no columns were dropped. | `schema_evolution = strict` |

### Implementation in Soda (checks.yml)
```yaml
checks for dim_symbol:
  - row_count > 0
  - schema:
      name: strict_schema
      warn:
        when schema changes
```

## 3. Observability
*   **Azure Monitor**: Track Airflow DAG failures and Infrastructure health.
*   **Data Lineage**: dbt docs + Airflow integration to trace bad data back to the source.
