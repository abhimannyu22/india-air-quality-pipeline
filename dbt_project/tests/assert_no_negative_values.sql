select * from {{ ref('fct_daily_readings') }}
where value < 0 and parameter <> 'temperature'