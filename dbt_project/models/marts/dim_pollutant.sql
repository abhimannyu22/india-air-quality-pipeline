select * from (values
    ('pm25', 'PM2.5', 'ug/m3', true),
    ('pm10', 'PM10', 'ug/m3', true),
    ('no2', 'Nitrogen dioxide', 'ug/m3', true),
    ('so2', 'Sulphur dioxide', 'ug/m3', true),
    ('co', 'Carbon monoxide', 'mg/m3', true),
    ('o3', 'Ozone', 'ug/m3', true),
    ('temperature', 'Temperature', 'c', false),
    ('relativehumidity', 'Relative humidity', '%', false)
) as t(parameter, pollutant_name, units, used_in_aqi)