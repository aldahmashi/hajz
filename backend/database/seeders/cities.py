"""The 14 Hajz cities (docs/01-planning.md, section 8).

tax_rate is a simplified demo value, not a legal tax rate (BR-PRC-03).
The import sets snapshot_date, source_url and cover photo per city.
"""

from __future__ import annotations

from database.seeders.helpers import upsert_many

COLUMNS = ("slug", "name", "country", "country_code", "region", "currency", "timezone", "tax_rate", "lat", "lng")

CITIES = [
    ("tokyo",          "Tokyo",          "Japan",          "JP", "Asia",     "JPY", "Asia/Tokyo",          "0.1000",  "35.676200",  "139.650300"),
    ("bangkok",        "Bangkok",        "Thailand",       "TH", "Asia",     "THB", "Asia/Bangkok",        "0.0700",  "13.756300",  "100.501800"),
    ("singapore",      "Singapore",      "Singapore",      "SG", "Asia",     "SGD", "Asia/Singapore",      "0.0900",  "1.352100",   "103.819800"),
    ("taipei",         "Taipei",         "Taiwan",         "TW", "Asia",     "TWD", "Asia/Taipei",         "0.0500",  "25.033000",  "121.565400"),
    ("istanbul",       "Istanbul",       "Turkey",         "TR", "Europe",   "TRY", "Europe/Istanbul",     "0.1200",  "41.008200",  "28.978400"),
    ("london",         "London",         "United Kingdom", "GB", "Europe",   "GBP", "Europe/London",       "0.2000",  "51.507400",  "-0.127800"),
    ("paris",          "Paris",          "France",         "FR", "Europe",   "EUR", "Europe/Paris",        "0.1000",  "48.856600",  "2.352200"),
    ("barcelona",      "Barcelona",      "Spain",          "ES", "Europe",   "EUR", "Europe/Madrid",       "0.1000",  "41.387400",  "2.168600"),
    ("rome",           "Rome",           "Italy",          "IT", "Europe",   "EUR", "Europe/Rome",         "0.1000",  "41.902800",  "12.496400"),
    ("new-york-city",  "New York City",  "United States",  "US", "Americas", "USD", "America/New_York",    "0.1475",  "40.712800",  "-74.006000"),
    ("mexico-city",    "Mexico City",    "Mexico",         "MX", "Americas", "MXN", "America/Mexico_City", "0.1600",  "19.432600",  "-99.133200"),
    ("rio-de-janeiro", "Rio de Janeiro", "Brazil",         "BR", "Americas", "BRL", "America/Sao_Paulo",   "0.0500",  "-22.906800", "-43.172900"),
    ("cape-town",      "Cape Town",      "South Africa",   "ZA", "Africa",   "ZAR", "Africa/Johannesburg", "0.1500",  "-33.924900", "18.424100"),
    ("sydney",         "Sydney",         "Australia",      "AU", "Oceania",  "AUD", "Australia/Sydney",    "0.1000",  "-33.868800", "151.209300"),
]


def seed(cursor) -> None:
    upsert_many(
        cursor,
        "cities",
        [dict(zip(COLUMNS, city, strict=True)) for city in CITIES],
        key_columns=("slug",),
        update_columns=COLUMNS[1:],
    )
