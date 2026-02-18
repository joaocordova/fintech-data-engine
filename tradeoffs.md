# Project Nexus: Trade-off Analysis & Architectural Decisions

## 1. Architecture: Medallion (Lakehouse) vs. Flat Warehouse
**Decision: Medallion Architecture (Bronze -> Silver -> Gold)**

| Feature | Medallion (Lakehouse) | Flat Warehouse | Why Medallion? |
| :--- | :--- | :--- | :--- |
| **History** | Keeps raw history (Bronze) forever (immutable). | often destructively updates or discards raw. | **Auditability**: If we find a bug in transformation logic 6 months later, we can reprocess purely from Bronze without re-fetching from source. |
| **Schema** | Schema-on-Read (Bronze) -> Schema-on-Write (Silver/Gold). | Schema-on-Write (Always). | **Flexibility**: We can ingest "garbage" or changing APIs into Bronze without breaking the pipeline, then handle evolution in Silver. |
| **Cost** | Cheap object storage (ADLS Gen2). | Expensive compute+storage coupling. | **Cost**: Storing TBs of raw market ticks in Postgres is prohibitively expensive compared to Parquet on ADLS. |

## 2. Serving Layer: Azure Postgres vs. Snowflake/Synapse
**Decision: Azure Database for PostgreSQL**

*   **Why not Snowflake/Synapse?**
    *   **Overkill for High-Frequency Aggregates**: Snowflake is an OLAP beast. For serving a dashboard that requests "last 5 minutes of sentiment", the latency overhead of a warehouse can be higher than a tuned RDBMS.
    *   **Cost**: Running a Synapse Dedicated Pool 24/7 for a dashboard is expensive. Postgres Flexible Server allows burstable compute.
    *   **Concurrency**: Postgres handles high-concurrency "Web App" type queries (thousands of users refreshing dashboards) better (and cheaper) than Warehouses designed for heavy analytical scans.
    *   **"Senior" Reasoning**: While Snowflake is better for *analyzing* petabytes, Postgres is better for *serving* the "Gold" layer to an application/API.

## 3. Orchestration: Apache Airflow vs. Azure Data Factory (ADF)
**Decision: Apache Airflow (on AKS/ACI)**

*   **Complexity**: ADF is great for simple "Copy Data" activities. Project Nexus requires complex Python logic (Data Contracts, custom API merging, detailed logging). Airflow allows "Code as Configuration".
*   **Dynamic Dependencies**: Airflow's DAGs allow dynamic task generation (e.g., "spawn a task for each stock symbol found in config"). ADF is more static.
*   **Vendor Lock-in**: Airflow is open source and portable. ADF is Azure-only. A Senior Architect mitigates lock-in risk.

## 4. Cost Optimization Strategy
*   **Lifecycle Management (ADLS)**:
    *   Rule: Move Bronze data > 30 days to Cool Tier. > 180 days to Archive Tier.
*   **Compute (AKS/Postgres)**:
    *   Use **Spot Instances** for the Airflow Worker application (stateless, tolerant to eviction).
    *   Use **Burstable (B-series)** for Postgres Dev environment; Reserved Instances for Prod.
