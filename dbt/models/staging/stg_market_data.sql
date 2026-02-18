with source as (
    select * from {{ source('bronze', 'market_data') }}
),

renamed as (
    select
        symbol,
        cast(timestamp as timestamp) as event_time,
        cast(open as decimal(10,2)) as open_price,
        cast(high as decimal(10,2)) as high_price,
        cast(low as decimal(10,2)) as low_price,
        cast(close as decimal(10,2)) as close_price,
        cast(volume as integer) as volume,
        ingestion_time
    from source
)

select * from renamed
