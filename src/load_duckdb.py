import duckdb

# DuckDB is a whole database stored in one file. No server needed.
con = duckdb.connect("data/warehouse.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
con.execute("CREATE SCHEMA IF NOT EXISTS silver")

# BRONZE: one row per daily reading, with the original JSON kept as text.
# CREATE OR REPLACE means we rebuild from the files each run, so running
# this twice never creates duplicates (idempotent).
con.execute("""
CREATE OR REPLACE TABLE bronze.measurements AS
SELECT
    sensor_id, location_id, city, station, parameter, units, fetched_at,
    unnest(results) AS payload
FROM read_json(
    'data/bronze/measurements/*.json',
    columns = {
        sensor_id: 'BIGINT', location_id: 'BIGINT', city: 'VARCHAR',
        station: 'VARCHAR', parameter: 'VARCHAR', units: 'VARCHAR',
        fetched_at: 'VARCHAR', results: 'JSON[]'
    }
)
""")

# SILVER: pick out the fields we need, give them proper types, and clean up.
con.execute("""
CREATE OR REPLACE TABLE silver.readings AS
SELECT
    sensor_id,
    location_id,
    city,
    station,
    parameter,
    units,
    -- the first 10 characters of the local time string are the date (YYYY-MM-DD)
    CAST(left(json_extract_string(payload, '$.period.datetimeFrom.local'), 10) AS DATE)
        AS reading_date,
    TRY_CAST(json_extract_string(payload, '$.summary.avg') AS DOUBLE) AS avg_value,
    TRY_CAST(json_extract_string(payload, '$.summary.min') AS DOUBLE) AS min_value,
    TRY_CAST(json_extract_string(payload, '$.summary.max') AS DOUBLE) AS max_value,
    TRY_CAST(json_extract_string(payload, '$.coverage.percentCoverage') AS DOUBLE)
        AS coverage_pct,
    CAST(fetched_at AS TIMESTAMPTZ) AS fetched_at
FROM bronze.measurements
WHERE json_extract_string(payload, '$.summary.avg') IS NOT NULL   -- drop empty days
-- if the same sensor+day appears twice, keep only the newest copy
QUALIFY row_number() OVER (
    PARTITION BY sensor_id, reading_date ORDER BY fetched_at DESC
) = 1
""")

print("bronze rows:", con.execute("SELECT count(*) FROM bronze.measurements").fetchone()[0])
print("silver rows:", con.execute("SELECT count(*) FROM silver.readings").fetchone()[0])
print()
print(con.execute("""
    SELECT city, count(DISTINCT station) AS stations, count(*) AS rows,
           min(reading_date) AS first_day, max(reading_date) AS last_day
    FROM silver.readings GROUP BY city ORDER BY city
""").df().to_string(index=False))
print()
print(con.execute("""
    SELECT parameter, units, count(*) AS rows
    FROM silver.readings GROUP BY 1, 2 ORDER BY 1, 2
""").df().to_string(index=False))