from unittest.mock import MagicMock

import pytest

from iteradraw.core.application.config import ApplicationConfiguration
from iteradraw.core.domain.repositories.directory_repository import \
    SQLite3DirectoryRepository
from iteradraw.core.domain.repositories.folder_repository import \
    SQLite3FolderRepository
from iteradraw.core.infrastructure.persistence.schema import SCHEMA
from iteradraw.core.infrastructure.persistence.sqlite3_database import \
    SQLite3Database
from iteradraw.core.infrastructure.persistence.unit_of_work import \
    SQLite3UnitOfWork, SQLite3UnitOfWorkFactory


@pytest.fixture(scope="session")
def app_config() -> ApplicationConfiguration:
    mock_config = MagicMock(spec=ApplicationConfiguration)
    mock_config.db_path = ":memory:"
    mock_config.crawler_batch_size = 5000
    return mock_config


@pytest.fixture(scope="function")
def sqlite_database_in_memory(app_config) -> SQLite3Database:
    database = SQLite3Database(
        app_config=app_config
    )
    database.open()
    database.executescript(SCHEMA)
    return database


@pytest.fixture(scope="function")
def sqlite_folder_repo(sqlite_database_in_memory) -> SQLite3FolderRepository:
    database = sqlite_database_in_memory
    folder_repo = SQLite3FolderRepository(database)
    return folder_repo


@pytest.fixture(scope="function")
def sqlite_directory_repo(
        sqlite_database_in_memory
) -> SQLite3DirectoryRepository:
    database = sqlite_database_in_memory
    dir_repo = SQLite3DirectoryRepository(database)
    return dir_repo


@pytest.fixture(scope="function")
def sqlite_unit_of_work_factory(
        sqlite_database_in_memory,
        sqlite_folder_repo,
        sqlite_directory_repo,
):
    uow_factory = SQLite3UnitOfWorkFactory(
        database=sqlite_database_in_memory,
        folder_repo=sqlite_folder_repo,
        dir_repo=sqlite_directory_repo,
    )
    return uow_factory


@pytest.fixture(scope="function")
def sqlite_unit_of_work(
        sqlite_database_in_memory,
        sqlite_folder_repo,
        sqlite_directory_repo
) -> SQLite3UnitOfWork:
    uow = SQLite3UnitOfWork(
        database=sqlite_database_in_memory,
        folder_repo=sqlite_folder_repo,
        dir_repo=sqlite_directory_repo,
    )
    return uow


@pytest.fixture(scope="function")
def make_temp_dir_tree(tmp_path_factory):
    roots = []
    for k in range(3):
        temp_dir = tmp_path_factory.mktemp("root_dir_", numbered=True)
        roots.append(temp_dir)
        for i in range(10):
            file2 = temp_dir / f"{i}.png"
            file2.touch()
            local_dir = temp_dir / f"sub{i}"
            local_dir.mkdir()
            for j in range(10):
                file1 = local_dir / f"sub{i}{j}.jpg"
                file1.touch()
    return roots
