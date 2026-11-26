-- "Above safe limit" = city AQI over 100 (worse than Satisfactory)
select
    city,
    cast(date_trunc('month', reading_date) as date) as month,
    round(avg(avg_aqi), 1) as avg_aqi,
    max(avg_aqi) as worst_day_aqi,
    count(*) as days_with_data,
    count(*) filter (where avg_aqi > 100) as days_above_safe_limit,
    round(100.0 * count(*) filter (where avg_aqi > 100) / count(*), 1) as pct_days_above_safe_limit
from {{ ref('agg_city_daily') }}
group by city, date_trunc('month', reading_date)