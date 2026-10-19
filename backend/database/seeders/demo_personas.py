"""Demo personas for one-click recruiter demos (BR-DEMO, AU-5).

No password: personas log in with one click (BR-DEMO-01). Their interaction
history is generated after the listing import (DA-5).
"""

from __future__ import annotations

from datetime import UTC, datetime

from database.seeders.helpers import upsert_many

PERSONAS = [
    {
        "persona_key": "budget_backpacker",
        "email": "backpacker@demo.hajz.app",
        "full_name": "Lina (Budget Backpacker)",
        "persona_summary": "Cheap private rooms near transit in Bangkok, Istanbul and Mexico City",
        "preferred_currency": "USD",
    },
    {
        "persona_key": "luxury_couple",
        "email": "couple@demo.hajz.app",
        "full_name": "Omar and Sara (Luxury Couple)",
        "persona_summary": "High-rated entire homes with a view in Paris, Rome and Sydney",
        "preferred_currency": "EUR",
    },
    {
        "persona_key": "remote_worker",
        "email": "remote@demo.hajz.app",
        "full_name": "Kenji (Remote Worker)",
        "persona_summary": "Long stays with a dedicated workspace and fast wifi in Tokyo, Taipei and London",
        "preferred_currency": "JPY",
    },
    {
        "persona_key": "family_traveller",
        "email": "family@demo.hajz.app",
        "full_name": "The Garcia Family",
        "persona_summary": "Spacious homes with a kitchen and crib in Barcelona, Cape Town and New York City",
        "preferred_currency": "USD",
    },
]


def seed(cursor) -> None:
    verified_at = datetime.now(UTC).replace(tzinfo=None, microsecond=0)
    upsert_many(
        cursor,
        "users",
        [
            {
                **persona,
                "password_hash": None,
                "role": "guest",
                "is_demo": True,
                "email_verified_at": verified_at,
            }
            for persona in PERSONAS
        ],
        key_columns=("persona_key",),
        update_columns=("email", "full_name", "persona_summary", "preferred_currency"),
    )
