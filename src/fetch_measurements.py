import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from openaq_client import get_all_pages

BACKFILL_DAYS = 90  # first run: how far back to go

OUT_DIR = Path("data/bronze/measurements")
OUT_DIR.mkdir(parents=True, exist_ok=True)

stations = json.loads(Path("data/selected_stations.json").read_text())
now = datetime.now(timezone.utc)

for st in stations:
    for sensor in st["sensors"]:
        file = OUT_DIR / f'{sensor["sensor_id"]}.json'

        # Keep results in a dict keyed by day. Re-fetching the same day just
        # overwrites it, so running twice never creates duplicates (idempotent).
        by_day = {}
        if file.exists():
            old = json.loads(file.read_text())
            by_day = {r["period"]["datetimeFrom"]["utc"]: r for r in old["results"]}

        if by_day:
            # Incremental run: only ask for new data. Start 2 days before the
            # newest day we have, because late readings sometimes get corrected.
            newest = max(by_day)
            start = datetime.fromisoformat(newest.replace("Z", "+00:00")) - timedelta(days=2)
        else:
            start = now - timedelta(days=BACKFILL_DAYS)  # first run: backfill

        # /days returns one pre-averaged row per day, much smaller than raw hourly data
        rows = get_all_pages(
            f'/sensors/{sensor["sensor_id"]}/days',
            {"datetime_from": start.isoformat(), "datetime_to": now.isoformat()},
            page_size=1000,
        )
        for r in rows:
            by_day[r["period"]["datetimeFrom"]["utc"]] = r

        record = {
            "city": st["city"], "location_id": st["location_id"],
            "station": st["name"], "sensor_id": sensor["sensor_id"],
            "parameter": sensor["parameter"], "units": sensor["units"],
            "fetched_at": now.isoformat(),
            "results": list(by_day.values()),
        }
        file.write_text(json.dumps(record))

    print(f'{st["city"]} - {st["name"]}: done')