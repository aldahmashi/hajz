"""Exchange rates: units of currency per 1 USD.

Placeholder snapshot. The Inside Airbnb import replaces it with a dated
snapshot before converting listing prices (BR-PRC-02).
"""

from __future__ import annotations

from database.seeders.helpers import upsert_many

AS_OF = "2026-10-01"

RATES = {
    "USD": "1.000000",
    "JPY": "150.000000",
    "THB": "33.000000",
    "SGD": "1.300000",
    "TWD": "31.000000",
    "TRY": "42.000000",
    "GBP": "0.750000",
    "EUR": "0.860000",
    "MXN": "18.500000",
    "BRL": "5.400000",
    "ZAR": "17.500000",
    "AUD": "1.520000",
    "SAR": "3.750000",
    "AED": "3.672500",
    "MYR": "4.200000",
}


def seed(cursor) -> None:
    upsert_many(
        cursor,
        "fx_rates",
        [{"currency": code, "usd_rate": rate, "as_of": AS_OF} for code, rate in RATES.items()],
        key_columns=("currency",),
        update_columns=("usd_rate", "as_of"),
    )
