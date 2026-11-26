-- Fact table: one row per station, day and pollutant.
-- If a station has two sensors for the same pollutant, we average them.
select
    location_id,
    city,
    station,
    reading_date,
    parameter,
    avg(value)        as value,
    min(units)        as units,
    avg(coverage_pct) as coverage_pct,
    count(*)          as sensor_count
from {{ ref('stg_readings') }}
group by location_id, city, station, reading_date, parameter