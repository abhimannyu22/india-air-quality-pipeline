-- Indian AQI (CPCB method):
--   1. Each pollutant gets a sub-index by interpolating inside its band.
--   2. The day's AQI is the highest sub-index.
--   3. Valid only if 3+ pollutants were measured, including PM2.5 or PM10.
-- Simplification: we use daily averages for all pollutants (the official method
-- uses 8-hour maximums for CO and O3). We also skip days with under 66% coverage.

with sub_indices as (
    select
        r.location_id, r.city, r.station, r.reading_date, r.parameter,
        least(500,
            b.index_low + (b.index_high - b.index_low)
            * (r.value - b.bp_low) / (b.bp_high - b.bp_low)
        ) as sub_index
    from {{ ref('fct_daily_readings') }} r
    join {{ ref('aqi_breakpoints') }} b
      on r.parameter = b.parameter
     and r.value >= b.bp_low
     and (r.value < b.bp_high or b.index_high = 500)  -- top band has no upper limit
    where r.coverage_pct >= 66
),

daily as (
    select
        location_id, city, station, reading_date,
        count(*) as pollutants_measured,
        round(max(sub_index)) as aqi,
        arg_max(parameter, sub_index) as main_pollutant
    from sub_indices
    group by location_id, city, station, reading_date
    having count(*) >= 3
       and count(*) filter (where parameter in ('pm25', 'pm10')) >= 1
)

select
    *,
    case
        when aqi <= 50  then 'Good'
        when aqi <= 100 then 'Satisfactory'
        when aqi <= 200 then 'Moderate'
        when aqi <= 300 then 'Poor'
        when aqi <= 400 then 'Very Poor'
        else 'Severe'
    end as aqi_category
from daily