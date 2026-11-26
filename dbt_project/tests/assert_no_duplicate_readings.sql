select location_id, reading_date, parameter, count(*) as n
from {{ ref('fct_daily_readings') }}
group by 1, 2, 3
having count(*) > 1