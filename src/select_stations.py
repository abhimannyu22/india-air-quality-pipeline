import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Only keep these pollutants (names as OpenAQ spells them)
WANTED = {"pm25", "pm10", "no2", "so2", "co", "o3", "temperature", "relativehumidity"}
MAX_PER_CITY = 8

# "Active" = sent data in the last 7 days. Dead stations would waste our API calls.
cutoff = datetime.now(timezone.utc) - timedelta(days=7)

selected = []
for file in sorted(Path("data/bronze/locations").glob("*.json")):
    record = json.loads(file.read_text())
    candidates = []
    for st in record["results"]:
        last = (st.get("datetimeLast") or {}).get("utc")
        if not last or st.get("isMobile"):
            continue  # never reported, or a moving sensor
        if datetime.fromisoformat(last.replace("Z", "+00:00")) < cutoff:
            continue  # stopped reporting

        sensors = [
            {"sensor_id": s["id"], "parameter": s["parameter"]["name"],
             "units": s["parameter"]["units"]}
            for s in st["sensors"] if s["parameter"]["name"] in WANTED
        ]
        if sensors:
            candidates.append({"city": record["city"], "location_id": st["id"],
                               "name": st["name"], "sensors": sensors})

    # Stations measuring the most pollutants are the most useful
    candidates.sort(key=lambda c: len(c["sensors"]), reverse=True)
    chosen = candidates[:MAX_PER_CITY]
    selected.extend(chosen)
    print(f'{record["city"]}: {len(candidates)} active, kept {len(chosen)}')

Path("data/selected_stations.json").write_text(json.dumps(selected, indent=1))
print("Total sensors to fetch:", sum(len(s["sensors"]) for s in selected))