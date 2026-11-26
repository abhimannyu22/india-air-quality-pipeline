select
    city,
    count(distinct location_id) as station_count,
    min(reading_date) as first_reading_date,
    max(reading_date) as last_reading_date
from {{ ref('fct_daily_readings') }}
group by city