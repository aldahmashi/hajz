"""GET /api/health — liveness and database check (UptimeRobot, Render, M0 smoke test)."""

from __future__ import annotations

import logging

from flask import Blueprint, current_app
from sqlalchemy import text

from database.connection import get_ro_session
from helpers.response import error, ok

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    try:
        revision = get_ro_session().execute(text("SELECT version_num FROM alembic_version")).scalar()
    except Exception:
        logger.exception("Health check: database unreachable")
        return error("DATABASE_UNAVAILABLE", "Database is unreachable.", 503)

    return ok(
        {
            "status": "ok",
            "env": current_app.config["APP_ENV"],
            "database": "ok",
            "migration": revision,
        }
    )
