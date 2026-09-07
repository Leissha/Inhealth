from __future__ import annotations

from collections.abc import Generator
from typing import Any

import pymysql
from pymysql.connections import Connection

from backend.app.config import get_settings


from fastapi import HTTPException, status


def create_connection() -> Connection:
    settings = get_settings()
    return pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=5,
    )


def get_db_connection() -> Generator[Any, None, None]:
    try:
        connection = create_connection()
    except pymysql.MySQLError as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {err}",
        ) from err

    try:
        yield connection
    finally:
        connection.close()
