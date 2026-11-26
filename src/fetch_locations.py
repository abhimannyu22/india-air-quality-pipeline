import json
from datetime import datetime, timezone
from pathlib import Path

from openaq_client import get_all_pages

# Centre point of each city. We search 25 km around each one.
CITIES = {
    "Mumbai": "19.0760,72.8777",
    "Delhi": "28.6139,77.2090",
    "Bangalore": "12.9716,77.5946",
    "Hyderabad": "17.3850,78.4867",
    "Kolkata": "22.5726,88.3639",
}

# Bronze layer: raw API responses saved exactly as received
OUT_DIR = Path("data/bronze/locations")
OUT_DIR.mkdir(parents=True, exist_ok=True)

for city, coords in CITIES.items():
    stations = get_all_pages("/locations", {"coordinates": coords, "radius": 25000})

    # We wrap the raw data with the city and fetch time, so we know where it came from
    record = {
        "city": city,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "results": stations,
    }
    (OUT_DIR / f"{city.lower()}.json").write_text(json.dumps(record))
    print(f"{city}: {len(stations)} stations saved")