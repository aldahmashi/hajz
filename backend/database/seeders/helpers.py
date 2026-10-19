from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def upsert_many(
    cursor,
    table: str,
    rows: Iterable[Mapping[str, Any]],
    key_columns: tuple[str, ...],
    update_columns: tuple[str, ...],
) -> None:
    for row in rows:
        where_clause = " AND ".join(f"{column} = %s" for column in key_columns)
        cursor.execute(
            f"SELECT 1 FROM {table} WHERE {where_clause} LIMIT 1",
            tuple(row[column] for column in key_columns),
        )
        exists = cursor.fetchone() is not None

        if exists:
            set_clause = ", ".join(f"{column} = %s" for column in update_columns)
            cursor.execute(
                f"UPDATE {table} SET {set_clause} WHERE {where_clause}",
                tuple(row[column] for column in update_columns)
                + tuple(row[column] for column in key_columns),
            )
        else:
            columns = tuple(row.keys())
            placeholders = ", ".join(["%s"] * len(columns))
            column_list = ", ".join(columns)
            cursor.execute(
                f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})",
                tuple(row[column] for column in columns),
            )


def get_id(cursor, table: str, id_column: str, key_column: str, key_value: Any) -> int:
    cursor.execute(f"SELECT {id_column} FROM {table} WHERE {key_column} = %s", (key_value,))
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError(f"Missing seed dependency: {table}.{key_column}={key_value}")
    return int(row[0])
