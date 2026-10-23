from __future__ import annotations

import manage


def test_load_env_strips_whitespace_like_the_app_config(monkeypatch):
    # A value pasted into the Render dashboard with a trailing newline once made
    # manage.py create database "hajz\n" while the app connected to "hajz".
    for key in ("DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("MYSQL_DB", " db.example.com : app.root : secret : 4000 : hajz \n")

    manage._load_env()

    assert manage.os.environ["DB_HOST"] == "db.example.com"
    assert manage.os.environ["DB_USER"] == "app.root"
    assert manage.os.environ["DB_PASSWORD"] == "secret"
    assert manage.os.environ["DB_PORT"] == "4000"
    assert manage.os.environ["DB_NAME"] == "hajz"
