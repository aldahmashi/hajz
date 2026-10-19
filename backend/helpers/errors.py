"""AppError and the handlers that turn every failure into the JSON envelope.

Services raise `AppError(code=...)` for business-rule violations; the code is
the one listed next to the rule in docs/04-business-rules.md.
"""

from __future__ import annotations

import logging

from flask import Flask
from werkzeug.exceptions import HTTPException

from helpers.response import error

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        return error(exc.code, exc.message, exc.status, exc.details)

    @app.errorhandler(HTTPException)
    def handle_http_error(exc: HTTPException):
        code = (exc.name or "HTTP_ERROR").upper().replace(" ", "_")
        return error(code, exc.description or exc.name, exc.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        logger.exception("Unhandled error")
        return error("INTERNAL_ERROR", "Something went wrong. Please try again.", 500)
