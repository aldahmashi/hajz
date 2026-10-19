"""Tests run against a real, migrated MySQL database (MYSQL_DB).

Locally that is the Docker MySQL from docker-compose.yml; in CI it is the
MySQL service container in .github/workflows/ci.yml.
"""

from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
