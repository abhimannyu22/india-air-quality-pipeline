import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://api.openaq.org/v3"
HEADERS = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}


def get(path, params=None, max_retries=5):
    """Call the OpenAQ API. Retry if we are rate-limited or the server fails.

    Why: APIs fail sometimes. A pipeline that crashes on one hiccup is
    unreliable, so we wait and try again instead.
    """
    for attempt in range(1, max_retries + 1):
        response = requests.get(
            f"{BASE_URL}{path}", headers=HEADERS, params=params, timeout=30
        )
        if response.status_code == 200:
            time.sleep(1.1)  # small pause so we stay under the rate limit
            return response.json()
        if response.status_code in (429, 500, 502, 503, 504):
            wait = 2 ** attempt  # 2, 4, 8, 16, 32 seconds (exponential backoff)
            print(f"Got {response.status_code}, retrying in {wait}s...")
            time.sleep(wait)
            continue
        response.raise_for_status()  # any other error: stop and show it
    raise RuntimeError(f"Failed after {max_retries} tries: {path}")


def get_all_pages(path, params=None, page_size=100):
    """Keep asking for the next page until there is no more data.

    Why: the API returns limited rows per call, so we loop through pages.
    """
    params = dict(params or {})
    params["limit"] = page_size
    page = 1
    results = []
    while True:
        params["page"] = page
        data = get(path, params)
        results.extend(data["results"])
        if len(data["results"]) < page_size:  # last page reached
            return results
        page += 1