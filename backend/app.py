"""Flask application factory.

    Local:       python app.py              (Flask dev server on PORT, default 8000)
    Production:  gunicorn "app:create_app()"
"""

from __future__ import annotations

import logging

from flask import Flask
from flask_cors import CORS

from config import Config, get_config
from database.connection import close_sessions, init_db
from helpers.errors import register_error_handlers
from routes import register_blueprints


def create_app(config: type[Config] | None = None) -> Flask:
    config = config or get_config()

    app = Flask(__name__)
    app.config.from_object(config)
    app.json.sort_keys = False

    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Production traffic is same-origin through the Vercel /api rewrite, so CORS
    # only matters for local development and preview deployments.
    CORS(app, origins=list(config.ALLOWED_ORIGINS), supports_credentials=True)

    init_db(app)
    app.teardown_appcontext(close_sessions)

    register_error_handlers(app)
    register_blueprints(app)
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=application.config["PORT"], debug=application.config["DEBUG"])
