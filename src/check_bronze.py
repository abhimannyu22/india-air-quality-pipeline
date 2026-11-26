import json
from pathlib import Path

files = list(Path("data/bronze/measurements").glob("*.json"))
total = 0
empty = 0
sample = None
for f in files:
    rec = json.loads(f.read_text())
    n = len(rec["results"])
    total += n
    if n == 0:
        empty += 1
    elif sample is None:
        sample = (rec["city"], rec["station"], rec["parameter"], rec["results"][0])

print("Sensor files:", len(files))
print("Sensors with no data:", empty)
print("Total daily rows:", total)
print("Sample:", json.dumps(sample, indent=1))