import sqlite3
from typing import (
    Iterable,
    Callable,
    Optional,
    Any,
)

from iteradraw.core.domain.models.session import Session
from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database

from iteradraw.core.domain.exceptions import CommitError
from iteradraw.interfaces import SessionRepository

"""
Repository layer for persistence of domain models such as FolderSet, TimerSet,
and aggregate roots like Session.

Repositories act as the boundary between the domain/application layers and the
underlying persistence mechanisms (e.g. JSON, SQLite). They expose operations
in domain terms — load, save, update — without leaking any storage details.

Each repository encapsulates its respective model’s persistence behavior,
providing better modularity and Separation of Concerns.

Classes:
    SQLSessionRepository: Coordinates FolderRepository and TimerRepository
                       to persist or reconstruct Session aggregates.

Usage:
    folder_repo = FolderRepository()
    last_folder_set = folder_repo.load()
    ...
    folder_repo.save(modified_folder_set)
"""


class SQLSessionRepository(SessionRepository):

    DB_SCHEMA = """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY,
        date INTEGER
    );
    CREATE TABLE IF NOT EXISTS session_images (
        session_id INTEGER NOT NULL ,
        image_id INTEGER,
        thumbnail_hash TEXT NOT NULL,
        timer INTEGER NOT NULL,
        position INTEGER NOT NULL,
        note TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        ON DELETE CASCADE,
        FOREIGN KEY (image_id) REFERENCES images(image_id)
    );
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.database:
            try:
                self.database.close()
            finally:
                self.database = None

    def __init__(
        self,
        database: SQLite3Database,
        on_insert: Callable = None,
        on_remove: Callable = None,
        on_mark_seen: Callable = None,
    ) -> None:
        self.database = database
        self.on_insert = on_insert
        self.on_remove = on_remove
        self.on_mark_seen = on_mark_seen

        self._setup_schema()
        self._configure_connection()

    def initialize(self) -> None:
        """Open the connection and ensure the schema exists."""
        self.setup_schema()  # create table if it isn’t there

    def _clear_all(self) -> None:
        """Drop the table – caller should call `setup_schema` afterwards."""
        query = "DROP TABLE IF EXISTS image_paths"
        with self.database:
            self._execute(query)

    def _setup_schema(self, db_schema: str | None = None) -> None:
        """Create `image_paths` with the supplied (or default) schema."""
        schema = db_schema or self.DB_SCHEMA
        query = f"CREATE TABLE IF NOT EXISTS image_paths ({schema})"
        with self.database:
            self._execute(query)

    def _insert_rows(self, rows: Iterable[tuple[Any, ...]]) -> int:
        cursor = self.database.cursor()
        cursor.executemany(
            """
            INSERT OR IGNORE INTO image_paths (path, randid, mtime)
            VALUES (?, ?, ?)
            """,
            rows,
        )
        inserted = cursor.rowcount
        cursor.close()
        if self.on_insert:
            self.on_insert()
        return inserted

    def _remove_rows(self, paths: Iterable[str]) -> int:
        with self.database:
            self.database.executemany(
                """
                DELETE FROM image_paths
                WHERE path = ?
                """,
                [(p,) for p in paths],
            )
            cur = self.database.execute("SELECT changes()")
            removed = cur.fetchone()
        if self.on_remove:
            self.on_remove()
        return removed[0] or 0

    def mark_seen(self, paths: Iterable[str], seen: bool = True) -> int:
        """
        Set the `seen` flag for the supplied paths.
        `paths` is an iterable of path strings.
        """
        with self.database:
            self.database.executemany(
                """
                UPDATE image_paths
                SET seen = ?
                WHERE path = ?
                """,
                [(int(seen), p) for p in paths],
            )
            cur = self.database.execute("SELECT changes()")
            marked = cur.fetchone()
        if self.on_mark_seen:
            self.on_mark_seen()
        return marked[0] or 0

    def _shuffle(self) -> None:
        """
        Assign a new random float in [0, 1) to the `randid` column of each row.
        """
        query = """
            UPDATE image_paths
            SET randid = ABS(RANDOM()) / 9223372036854775808.0
        """
        with self.database:
            self._execute(query)

    # Non-default backend methods

    def _count_rows(self) -> int:
        cur = self._execute("SELECT COUNT(*) FROM image_paths")
        return cur.fetchone()[0] or 0

    def _commit(self) -> None:
        """Explicitly commit any pending transaction."""
        try:
            if self.database:
                self.database.commit()
                self.database.execute("PRAGMA wal_checkpoint(FULL);")
        except sqlite3.DatabaseError as e:
            raise CommitError("Failed to commit to database") from e