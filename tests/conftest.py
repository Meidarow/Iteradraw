from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from iteradraw.bootstrap import ALL_HANDLERS, register_command_handlers
from iteradraw.core.application.config import ApplicationConfiguration
from iteradraw.core.application.shell import ApplicationShell
from iteradraw.core.domain.models.folder import FolderSet
from iteradraw.core.domain.repositories.directory_repository import \
    SQLite3DirectoryRepository
from iteradraw.core.domain.repositories.folder_repository import \
    SQLite3FolderRepository
from iteradraw.core.infrastructure.buses.command_bus import CommandBus
from iteradraw.core.infrastructure.buses.event_bus import EventBus
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
def mock_event_bus() -> EventBus:
    event_bus = EventBus()
    return event_bus


@pytest.fixture(scope="function")
def mock_command_bus() -> CommandBus:
    command_bus = CommandBus()
    return command_bus


@pytest.fixture(scope="function")
def mock_bootstrap(
        sqlite_database_in_memory,
        sqlite_folder_repo,
        sqlite_directory_repo,
        sqlite_unit_of_work_factory,
        mock_event_bus,
        mock_command_bus,
) -> SimpleNamespace:
    kwargs = {
        "uow_factory": sqlite_unit_of_work_factory,
        "event_bus": mock_event_bus,
    }
    handler_instances = {}
    for handler_class in ALL_HANDLERS:
        handler_instances.setdefault(
            handler_class,
            handler_class(**kwargs)
        )
    register_command_handlers(mock_command_bus, handler_instances)
    shell = ApplicationShell(
        command_bus=mock_command_bus,
        event_bus=mock_event_bus,
        uow_factory=sqlite_unit_of_work_factory
    )
    return SimpleNamespace(
        shell=shell,
        event_bus=mock_event_bus,
        command_bus=mock_command_bus,
        uow_factory=sqlite_unit_of_work_factory,
    )

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


@pytest.fixture(scope="function")
def make_mock_folderset(
        sqlite_database_in_memory,
        sqlite_folder_repo,
        make_temp_dir_tree):
    def make(
            name: str = "Test Folder Set",
            dir_number: int = 0,
    ):
        db = sqlite_database_in_memory
        folder_repo = sqlite_folder_repo
        fs_id = folder_repo.create_folderset(name)
        folderset = FolderSet(
            id=fs_id,
            display_name=name
        )
        if not dir_number:
            return folderset

        temp_dir_tree = make_temp_dir_tree.copy()
        for i in range(dir_number):
            sample_dir = temp_dir_tree.pop()
            # Bypass DirectoryRepo to insert base node in DB
            query = """
            INSERT INTO directories (dir_name, crawl_time, mod_time) 
            VALUES (?, 0, 0)
            """
            db.execute(query, (str(sample_dir),))
            folderset = folderset.add(path=sample_dir)
        return folderset

    return make
