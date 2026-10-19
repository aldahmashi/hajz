from __future__ import annotations

from flask import Flask

from routes.health import health_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp, url_prefix="/api")
