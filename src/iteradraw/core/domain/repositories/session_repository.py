import sqlite3
from typing import (
    Iterable,
    Any,
)

from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database

from iteradraw.core.domain.exceptions import CommitError
from iteradraw.interfaces import SessionRepository


class SQLSessionRepository(SessionRepository):

    def __init__(
        self,
        database: SQLite3Database
    ) -> None:
        self.database = database