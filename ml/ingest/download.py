"""Step 1: download the newest listings.csv.gz for each city into data/raw/.

    python -m ml.ingest.download --dry-run          show what would be downloaded
    python -m ml.ingest.download                    all 14 cities
    python -m ml.ingest.download --city tokyo       one city

Only listings are saved whole. Reviews and calendars are 10x larger, so a later
step streams them and keeps only rows for the stays that survive cleaning.

Files land in data/raw/<city>/<snapshot-date>/listings.csv.gz (git-ignored).
data/raw/manifest.json records the snapshot and source URL per city, which the
import writes to cities.snapshot_date and cities.source_url.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

from ml.ingest.sources import CITY_PATHS, USER_AGENT, Snapshot, fetch_index, latest_snapshots

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"
MANIFEST_PATH = RAW_DIR / "manifest.json"
CHUNK_SIZE = 1 << 20


def target_path(snapshot: Snapshot, file: str = "listings") -> Path:
    return RAW_DIR / snapshot.city / snapshot.date / f"{file}.csv.gz"


def remote_size(url: str) -> int | None:
    response = requests.head(url, headers={"User-Agent": USER_AGENT}, timeout=30, allow_redirects=True)
    if response.status_code != 200:
        return None
    length = response.headers.get("Content-Length")
    return int(length) if length else None


def download(url: str, destination: Path) -> int:
    """Stream to a .part file and rename on success, so a broken download never looks complete."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    written = 0
    with requests.get(url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=60) as response:
        response.raise_for_status()
        with partial.open("wb") as file:
            for chunk in response.iter_content(CHUNK_SIZE):
                file.write(chunk)
                written += len(chunk)
    partial.replace(destination)
    return written


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def megabytes(size: int | None) -> str:
    return "?" if size is None else f"{size / 1_048_576:.1f} MB"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--city", choices=sorted(CITY_PATHS), action="append", help="limit to a city (repeatable)")
    parser.add_argument("--dry-run", action="store_true", help="list files and sizes without downloading")
    args = parser.parse_args(argv)

    snapshots = latest_snapshots(fetch_index())
    cities = args.city or list(CITY_PATHS)
    missing = [city for city in cities if city not in snapshots]
    if missing:
        print(f"No snapshot found on Inside Airbnb for: {', '.join(missing)}", file=sys.stderr)
        return 1

    manifest = load_manifest()
    total = 0
    for city in cities:
        snapshot = snapshots[city]
        url = snapshot.url("listings")
        destination = target_path(snapshot)

        if destination.exists():
            print(f"{city:<16} {snapshot.date}  already downloaded")
        elif args.dry_run:
            size = remote_size(url)
            total += size or 0
            print(f"{city:<16} {snapshot.date}  {megabytes(size):>9}  {url}")
            continue
        else:
            print(f"{city:<16} {snapshot.date}  downloading...", end="", flush=True)
            size = download(url, destination)
            total += size
            print(f" {megabytes(size)}")

        manifest[city] = {
            "snapshot_date": snapshot.date,
            "source_url": url,
            "path": destination.relative_to(ROOT_DIR).as_posix(),
        }

    if args.dry_run:
        print(f"\nWould download {megabytes(total)}. Nothing was written.")
        return 0

    save_manifest(manifest)
    print(f"\nDownloaded {megabytes(total)}. Manifest: {MANIFEST_PATH.relative_to(ROOT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
