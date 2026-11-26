-- days_since_last_reading is how we spot stations that stopped reporting
select
    location_id,
    any_value(city) as city,
    any_value(station) as station,
    min(reading_date) as first_reading_date,
    max(reading_date) as last_reading_date,
    date_diff('day', max(reading_date), current_date) as days_since_last_reading,
    date_diff('day', max(reading_date), current_date) <= 7 as is_active,
    count(distinct parameter) as pollutant_count
from {{ ref('fct_daily_readings') }}
group by location_id