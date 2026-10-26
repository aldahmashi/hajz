from __future__ import annotations

from ml.ingest.sources import CITY_PATHS, Snapshot, latest_snapshots

INDEX = """
<a href="https://data.insideairbnb.com/japan/kantō/tokyo/2026-06-20/data/listings.csv.gz">old</a>
<a href="https://data.insideairbnb.com/japan/kantō/tokyo/2026-09-25/data/listings.csv.gz">new</a>
<a href="https://data.insideairbnb.com/japan/kantō/tokyo/2026-09-25/data/reviews.csv.gz">reviews</a>
<a href="https://data.insideairbnb.com/canada/on/london/2026-09-30/data/listings.csv.gz">other London</a>
<a href="https://data.insideairbnb.com/united-kingdom/england/london/2026-09-17/data/listings.csv.gz">London</a>
"""


def test_picks_the_newest_snapshot_per_city():
    assert latest_snapshots(INDEX)["tokyo"].date == "2026-09-25"


def test_matches_the_full_path_not_just_the_city_name():
    london = latest_snapshots(INDEX)["london"]
    assert london.path == "united-kingdom/england/london"
    assert london.date == "2026-09-17"


def test_cities_missing_from_the_page_are_left_out():
    assert "paris" not in latest_snapshots(INDEX)


def test_url_percent_encodes_non_ascii_paths():
    url = Snapshot(city="tokyo", path=CITY_PATHS["tokyo"], date="2026-09-25").url("listings")
    assert url == "https://data.insideairbnb.com/japan/kant%C5%8D/tokyo/2026-09-25/data/listings.csv.gz"
