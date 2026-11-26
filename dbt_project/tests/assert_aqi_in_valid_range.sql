select * from {{ ref('fct_daily_aqi') }}
where aqi < 0 or aqi > 500