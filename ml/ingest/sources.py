"""Find the newest Inside Airbnb snapshot for each Hajz city.

Inside Airbnb publishes one folder per city and snapshot date:
    https://data.insideairbnb.com/<country>/<region>/<city>/<YYYY-MM-DD>/data/<file>.csv.gz
The get-the-data page links the newest snapshot of every city, so we read it
instead of hard-coding dates that go stale every quarter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote

import requests

INDEX_URL = "https://insideairbnb.com/get-the-data/"
DATA_HOST = "https://data.insideairbnb.com"
USER_AGENT = "HajzDataImport/1.0 (+https://github.com/aldahmashi/hajz)"

# Hajz city slug -> Inside Airbnb "<country>/<region>/<city>" path.
CITY_PATHS = {
    "tokyo": "japan/kantō/tokyo",
    "bangkok": "thailand/central-thailand/bangkok",
    "singapore": "singapore/sg/singapore",
    "taipei": "taiwan/northern-taiwan/taipei",
    "istanbul": "turkey/marmara/istanbul",
    "london": "united-kingdom/england/london",
    "paris": "france/ile-de-france/paris",
    "barcelona": "spain/catalonia/barcelona",
    "rome": "italy/lazio/rome",
    "new-york-city": "united-states/ny/new-york-city",
    "mexico-city": "mexico/df/mexico-city",
    "rio-de-janeiro": "brazil/rj/rio-de-janeiro",
    "cape-town": "south-africa/wc/cape-town",
    "sydney": "australia/nsw/sydney",
}


@dataclass(frozen=True)
class Snapshot:
    city: str
    path: str
    date: str

    def url(self, file: str) -> str:
        """Percent-encoded URL of one data file, e.g. file='listings'."""
        return f"{DATA_HOST}/{quote(self.path)}/{self.date}/data/{file}.csv.gz"


def latest_snapshots(index_html: str) -> dict[str, Snapshot]:
    """Newest snapshot date per city found in the index page HTML."""
    snapshots: dict[str, Snapshot] = {}
    for city, path in CITY_PATHS.items():
        pattern = re.escape(f"{DATA_HOST}/{path}/") + r"(\d{4}-\d{2}-\d{2})/data/listings\.csv\.gz"
        dates = re.findall(pattern, index_html)
        if dates:
            snapshots[city] = Snapshot(city=city, path=path, date=max(dates))
    return snapshots


def fetch_index() -> str:
    response = requests.get(INDEX_URL, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    # The page is UTF-8 but sends no charset, so requests would guess Latin-1
    # and mangle paths like "kantō" (Tokyo).
    return response.content.decode("utf-8")
