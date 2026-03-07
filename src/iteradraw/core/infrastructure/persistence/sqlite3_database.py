import sqlite3
from collections.abc import Sequence
from typing import (
    Any,
)

from iteradraw.core.application.config import ApplicationConfiguration

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
        self.connection = sqlite3.connect(self.db_path)

    def close(self) -> None:
        self.connection.close()

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def execute(self, query: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        return self.connection.execute(query, params)

    def executemany(self, query: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        return self.connection.executemany(query, params)

    def executescript(self, script: str) -> sqlite3.Cursor:
        return self.connection.executescript(script)