from __future__ import annotations

from database.seeders import amenities, cities, demo_personas, fx_rates

# Order matters when a seeder depends on rows from another one.
SEEDERS = [
    ("fx_rates", fx_rates.seed),
    ("cities", cities.seed),
    ("amenities", amenities.seed),
    ("demo_personas", demo_personas.seed),
]


def run_seeders(connection, logger=print) -> None:
    with connection.cursor() as cursor:
        for name, seed_func in SEEDERS:
            seed_func(cursor)
            logger(f"seeded {name}")
