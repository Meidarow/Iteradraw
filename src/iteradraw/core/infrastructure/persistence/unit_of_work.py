from typing import Type

from iteradraw.core.application.config import ApplicationConfiguration
from iteradraw.core.domain.repositories.directory_repository import \
    SQLite3DirectoryRepository
from iteradraw.core.domain.repositories.folder_repository import \
    SQLite3FolderRepository
from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database
from iteradraw.interfaces import UnitOfWork, UnitOfWorkFactory


class SQLite3UnitOfWorkFactory(UnitOfWorkFactory):
    def __init__(self, config: ApplicationConfiguration):
        self.config = config
        self.dir_repo = SQLite3DirectoryRepository
        self.folder_repo = SQLite3FolderRepository
        self.db = SQLite3Database

    def __call__(self) -> SQLite3UnitOfWork:
        database = self.db(self.config)
        return SQLite3UnitOfWork(
            database=database,
            dir_repo=self.dir_repo(database),
            folder_repo=self.folder_repo(database),
        )

class SQLite3UnitOfWork(UnitOfWork):
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
        self.database.close()

    def commit(self) -> None:
        self.database.commit()

    def rollback(self) -> None:
        self.database.rollback()