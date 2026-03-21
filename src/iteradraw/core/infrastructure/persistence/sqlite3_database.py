import sqlite3
from collections.abc import Sequence
from typing import (
    Any,
)

from iteradraw.core.application.config import ApplicationConfiguration
from iteradraw.core.domain.exceptions import DatabaseConnectionError
from iteradraw.interfaces import Database

"""
This module includes the default database solution for Iteradraw.

Contains:
SQLite3Database
"""


class SQLite3Database(Database):
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
        """
        Initializes database connection.

        SQLite does not allow for thread safety level (synchronous) to be
        changed during a transaction. Since autocommit = False always keeps a
        transaction open, here we briefly set autocommit = True, set thread
        safety level, then switch back to False. Explicit transaction control
        happens through commit() and rollback().
        """
        if not self.connection:
            self.connection = sqlite3.connect(
                self.db_path,
                autocommit=True,
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            script = """
            PRAGMA synchronous = NORMAL;
            PRAGMA journal_mode = WAL;
            PRAGMA temp_store = MEMORY;
            PRAGMA foreign_keys = ON;
            """
            self.connection.executescript(script)
            self.connection.autocommit = False

    def close(self) -> None:
        """
        Closes database connection.

        Notes: This should only be done at application teardown, the same
        connection can be reused in many transactions.
        """
        if self.connection:
            self.connection.close()
            self.connection = None

    def commit(self) -> None:
        """
        Commits changes.

        Closes transaction persisting changes and opens a new one.
        """
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        self.connection.commit()

    def rollback(self) -> None:
        """
        Rolls back changes.

        Closes transaction discarding changes and opens new one.
        """
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        self.connection.rollback()

    def execute(self, query: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        """
        Executes single SQL statement.

        Args:
            query: SQL statement string.
            params: Values plugged into slots (?) in statement.
        """
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        return self.connection.execute(query, params)

    def executemany(self, query: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        """
        Executes a statement repeatedly in a single transaction.

        Args:
            query: SQL statement string.
            params: Values plugged into slots (?) in statement.
         """
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        return self.connection.executemany(query, params)

    def executescript(self, script: str) -> sqlite3.Cursor:
        """
        Executes a series of statements.

        Args:
            script: SQL script string.
        """
        if not self.connection:
            raise DatabaseConnectionError("Connection not open")
        return self.connection.executescript(script)