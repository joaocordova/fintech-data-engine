{{
    config(
        materialized='incremental',
        unique_key='symbol',
        on_schema_change='fail'
    )
}}

with source as (
    select * from {{ ref('stg_market_data') }}
),

-- In a real SCD2, we would use dbt snapshots.
-- Here we demonstrate determining the "current" state of a symbol
latest_state as (
    select
        symbol,
        max(event_time) as last_updated,
        avg(close_price) as avg_price -- Example attribute
    from source
    group by symbol
)

select * from latest_state
