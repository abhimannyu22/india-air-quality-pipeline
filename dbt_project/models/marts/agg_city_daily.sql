select
    city,
    reading_date,
    round(avg(aqi)) as avg_aqi,
    max(aqi) as worst_station_aqi,
    count(*) as stations_reporting
from {{ ref('fct_daily_aqi') }}
group by city, reading_date