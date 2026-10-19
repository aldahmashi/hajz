"""Column types shared by the models, matching the MySQL types in migrations/.

Migrations are the source of truth for the schema. Models mirror them so the
services can query with SQLAlchemy, and `python manage.py migration-check`
fails if the two drift apart.
"""

from sqlalchemy import Enum
from sqlalchemy.dialects import mysql

UBigInt = mysql.BIGINT(unsigned=True)
UInt = mysql.INTEGER(unsigned=True)
USmallInt = mysql.SMALLINT(unsigned=True)
UTinyInt = mysql.TINYINT(unsigned=True)
Bool = mysql.TINYINT(display_width=1)


def enum(*values: str) -> Enum:
    """A native MySQL ENUM holding plain strings."""
    return Enum(*values, native_enum=True, create_constraint=False, validate_strings=True)
