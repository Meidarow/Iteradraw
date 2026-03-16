import sqlite3
from collections.abc import Sequence
from typing import (
    Any,
)

from iteradraw.core.application.config import ApplicationConfiguration
from iteradraw.core.domain.exceptions import DatabaseConnectionError

"""
This module includes the default database solution for Iteradraw.

Contains:
SQLite3Database
"""


class SQLite3Database:
    """
    SQLite3 implementation of the Iteradraw database backend.

    Handles connection and defines operations to consumers.
    """

    def __init__(
        self, app_config: ApplicationConfiguration
    ) -> None:
        self.db_path = app_config.db_path
        self.connection = None

    def __enter__(self) -> SQLite3Database:
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.connection.__exit__(exc_type, exc_val, exc_tb)

    def open(self) -> None:
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path, autocommit=False)
            self.connection.row_factory = sqlite3.Row
            script = """
            COMMIT;
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;
            PRAGMA temp_storage = MEMORY;
            PRAGMA foreign_keys = ON;
            """
            self.connection.executescript(script)

    def close(self) -> None:
        if self.connection:
            self.connection.close()

    def commit(self) -> None:
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        self.connection.commit()

    def rollback(self) -> None:
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        self.connection.rollback()

    def execute(self, query: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        return self.connection.execute(query, params)

    def executemany(self, query: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        return self.connection.executemany(query, params)

    def executescript(self, script: str) -> sqlite3.Cursor:
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        return self.connection.executescript(script)