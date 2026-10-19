"""JSON response envelope shared by every endpoint.

    success  {"data": ...}
    failure  {"error": {"code": "BOOKING_DATES_TAKEN", "message": "...", "details": {...}}}
"""

from __future__ import annotations

from typing import Any

from flask import jsonify
from flask.typing import ResponseReturnValue


def ok(data: Any = None, status: int = 200) -> ResponseReturnValue:
    return jsonify({"data": data}), status


def error(code: str, message: str, status: int, details: dict | None = None) -> ResponseReturnValue:
    body: dict[str, Any] = {"code": code, "message": message}
    if details:
        body["details"] = details
    return jsonify({"error": body}), status
