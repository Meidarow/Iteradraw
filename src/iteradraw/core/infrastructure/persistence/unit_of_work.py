from __future__ import annotations

from iteradraw.core.domain.repositories.directory_repository import \
    SQLite3DirectoryRepository
from iteradraw.core.domain.repositories.folder_repository import \
    SQLite3FolderRepository
from iteradraw.core.infrastructure.persistence.sqlite3_database import \
    SQLite3Database
from iteradraw.interfaces import UnitOfWork, UnitOfWorkFactory


class SQLite3UnitOfWorkFactory(UnitOfWorkFactory):
    def __init__(
            self,
            database: SQLite3Database,
            dir_repo: SQLite3DirectoryRepository,
            folder_repo: SQLite3FolderRepository,
    ):
        self.db = database
        self.dir_repo = dir_repo
        self.folder_repo = folder_repo

    def __call__(self) -> SQLite3UnitOfWork:
        return SQLite3UnitOfWork(
            database=self.db,
            dir_repo=self.dir_repo,
            folder_repo=self.folder_repo,
        )

class SQLite3UnitOfWork(UnitOfWork):
    """
    Attributes:
        dir_repo: SQLite3DirectoryRepository
        folder_repo: SQLite3FolderRepository
        database: SQLite3Database
    """
    def __init__(
            self,
            dir_repo: SQLite3DirectoryRepository,
            folder_repo: SQLite3FolderRepository,
            database: SQLite3Database
            ):
        self.dir_repo = dir_repo
        self.folder_repo = folder_repo
        self.database = database

    def __enter__(self) -> SQLite3UnitOfWork:
        self.database.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.rollback()

    def commit(self) -> None:
        self.database.commit()

    def rollback(self) -> None:
        self.database.rollback()