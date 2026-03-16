from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database
from iteradraw.interfaces import DirectoryRepository, FolderRepository, SessionRepository


class UnitOfWork:
    def __init__(
            self,
            dir_repo: DirectoryRepository,
            folder_repo: FolderRepository,
            database: SQLite3Database
            ):
        self.dir_repo = dir_repo
        self.folder_repo = folder_repo
        self.database = database

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    def commit(self):
        self.database.commit()

    def rollback(self):
        self.database.rollback()
