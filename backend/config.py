"""Application configuration, read from environment variables.

Local development loads `backend/.env`. Deployed environments (Render) set the
same variables in the host dashboard.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SUPPORTED_ENVIRONMENTS = {"local", "test", "production"}


def setting(name: str, default: str = "", *, required: bool = False) -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value
    if required:
        raise RuntimeError(f"{name} is required. Set it in backend/.env or the host environment.")
    return default


def mysql_url(value: str) -> str:
    """Convert host:user:password:port:database into a SQLAlchemy URL."""
    parts = value.strip().split(":")
    if len(parts) != 5:
        raise RuntimeError("MYSQL_DB format: host:user:password:port:database")
    host, user, password, port, database = (part.strip() for part in parts)
    if not all((host, user, port, database)):
        raise RuntimeError("MYSQL_DB requires host, user, port and database.")
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        raise RuntimeError("MYSQL_DB port must be between 1 and 65535.")
    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{int(port)}/{database}?charset=utf8mb4"
    )


APP_ENV = setting("APP_ENV", "local").lower()
if APP_ENV not in SUPPORTED_ENVIRONMENTS:
    raise RuntimeError(f"Unsupported APP_ENV: {APP_ENV}")


class Config:
    APP_ENV = APP_ENV
    IS_LOCAL = APP_ENV == "local"
    IS_PRODUCTION = APP_ENV == "production"
    DEBUG = IS_LOCAL
    PORT = int(setting("PORT", "8000"))
    LOG_LEVEL = setting("LOG_LEVEL", "INFO").upper()

    DATABASE_URL = mysql_url(setting("MYSQL_DB", required=True))
    DATABASE_URL_RO = mysql_url(setting("MYSQL_DB_RO")) if setting("MYSQL_DB_RO") else DATABASE_URL
    DB_SSL_CA = setting("DB_SSL_CA")

    ALLOWED_ORIGINS = tuple(
        origin.strip()
        for origin in setting("ALLOWED_ORIGINS", "http://localhost:4200").split(",")
        if origin.strip()
    )


def get_config() -> type[Config]:
    return Config
