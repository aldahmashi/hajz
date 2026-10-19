"""Canonical amenities. The importer maps raw Inside Airbnb amenity strings
onto these names. is_filter = shown as a search filter in the UI.
"""

from __future__ import annotations

from database.seeders.helpers import upsert_many

# (name, category, is_filter)
AMENITIES = [
    ("Wifi",                    "essentials",    True),
    ("Air conditioning",        "essentials",    True),
    ("Heating",                 "essentials",    False),
    ("Hot water",               "essentials",    False),
    ("Essentials",              "essentials",    False),
    ("Bed linens",              "essentials",    False),
    ("Hair dryer",              "essentials",    False),
    ("Iron",                    "essentials",    False),
    ("Washer",                  "essentials",    True),
    ("Dryer",                   "essentials",    False),
    ("Self check-in",           "essentials",    True),
    ("Elevator",                "essentials",    False),
    ("Kitchen",                 "kitchen",       True),
    ("Refrigerator",            "kitchen",       False),
    ("Microwave",               "kitchen",       False),
    ("Cooking basics",          "kitchen",       False),
    ("Coffee maker",            "kitchen",       False),
    ("Dishwasher",              "kitchen",       False),
    ("Oven",                    "kitchen",       False),
    ("Breakfast",               "kitchen",       False),
    ("Dedicated workspace",     "work",          True),
    ("Long term stays allowed", "work",          False),
    ("Pool",                    "outdoor",       True),
    ("Hot tub",                 "outdoor",       False),
    ("Patio or balcony",        "outdoor",       True),
    ("Backyard",                "outdoor",       False),
    ("BBQ grill",               "outdoor",       False),
    ("Beachfront",              "outdoor",       True),
    ("Waterfront",              "outdoor",       False),
    ("Gym",                     "entertainment", True),
    ("TV",                      "entertainment", False),
    ("Smoke alarm",             "safety",        False),
    ("Carbon monoxide alarm",   "safety",        False),
    ("Fire extinguisher",       "safety",        False),
    ("First aid kit",           "safety",        False),
    ("Crib",                    "family",        True),
    ("High chair",              "family",        False),
    ("Pets allowed",            "family",        True),
    ("Free parking",            "parking",       True),
    ("Paid parking",            "parking",       False),
    ("EV charger",              "parking",       False),
    ("Luggage dropoff allowed", "other",         False),
]


def seed(cursor) -> None:
    upsert_many(
        cursor,
        "amenities",
        [
            {"name": name, "category": category, "is_filter": is_filter}
            for name, category, is_filter in AMENITIES
        ],
        key_columns=("name",),
        update_columns=("category", "is_filter"),
    )
