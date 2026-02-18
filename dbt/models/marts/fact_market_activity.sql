{{
    config(
        materialized='incremental',
        unique_key='event_id',
        partition_by={
            "field": "event_date",
            "data_type": "date"
        }
    )
}}

with source as (
    select * from {{ ref('stg_market_data') }}
),

fact as (
    select
        md5(concat(symbol, event_time)) as event_id,
        symbol,
        event_time,
        date(event_time) as event_date,
        open_price,
        close_price,
        volume,
        (close_price - open_price) as daily_movement
    from source
    
    {% if is_incremental() %}
    -- this filter will only be applied on an incremental run
    where event_time > (select max(event_time) from {{ this }})
    {% endif %}
)

select * from fact
