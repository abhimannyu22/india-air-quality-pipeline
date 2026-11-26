import os
import requests
from dotenv import load_dotenv

# Read OPENAQ_API_KEY from the .env file, so the key never appears in the code
load_dotenv()
API_KEY = os.getenv("OPENAQ_API_KEY")

# OpenAQ expects the key in a header named X-API-Key
headers = {"X-API-Key": API_KEY}

# Ask for stations within 25 km of central Delhi (25 km is the maximum radius)
url = "https://api.openaq.org/v3/locations"
params = {"coordinates": "28.6139,77.2090", "radius": 25000, "limit": 5}

response = requests.get(url, headers=headers, params=params, timeout=30)

# 200 means success. 401 means the key is wrong.
print("Status:", response.status_code)

for station in response.json()["results"]:
    print(station["id"], station["name"])