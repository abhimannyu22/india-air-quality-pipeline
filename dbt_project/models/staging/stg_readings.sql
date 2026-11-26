-- Problem: gases arrive in two units (ppb and ug/m3), but the AQI formula
-- needs one. We convert ppb to ug/m3 using: ug/m3 = ppb * molecular_weight / 24.45
-- (24.45 = molar volume of air at 25 C). CO is then converted to mg/m3,
-- the unit the Indian AQI uses for CO.

with converted as (
    select
        sensor_id,
        location_id,
        city,
        station,
        parameter,
        reading_date,
        coverage_pct,
        case
            when parameter = 'no2' and units = 'ppb' then avg_value * 46.01 / 24.45
            when parameter = 'so2' and units = 'ppb' then avg_value * 64.07 / 24.45
            when parameter = 'o3'  and units = 'ppb' then avg_value * 48.00 / 24.45
            when parameter = 'co'  and units = 'ppb' then avg_value * 28.01 / 24.45 / 1000
            when parameter = 'co'                    then avg_value / 1000
            else avg_value
        end as value
    from {{ source('silver', 'readings') }}
)

select
    *,
    case
        when parameter = 'co' then 'mg/m3'
        when parameter = 'temperature' then 'c'
        when parameter = 'relativehumidity' then '%'
        else 'ug/m3'
    end as units
from converted
-- negative pollutant readings are sensor errors, so we drop them
where value is not null
  and (parameter = 'temperature' or value >= 0)