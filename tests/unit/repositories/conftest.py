from types import SimpleNamespace

import pytest

from iteradraw.core.application.config import ApplicationConfiguration
from iteradraw.core.domain.models.folder import FolderSet
from iteradraw.core.domain.repositories.folder_repository import SQLFolderRepository
from iteradraw.core.infrastructure.persistence.schema import SCHEMA
from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database


@pytest.fixture(scope="session")
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
def make_database_in_memory():
    database = SQLite3Database(
        app_config=ApplicationConfiguration()
    )
    database.open()
    database.executescript(SCHEMA)
    return database

@pytest.fixture(scope="function")
def setup(make_database_in_memory):
    db = make_database_in_memory
    repository = SQLFolderRepository(database=db)
    return SimpleNamespace(db=db, repository=repository)

@pytest.fixture(scope="function")
def make_folderset(setup, make_temp_dir_tree):
    def make(
            name: str = "Test Folder Set",
            dir_number: int = 0
    ):
        fs_id = setup.repository.create_folderset(name)
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
            setup.db.execute(query, (str(sample_dir),))
            folderset = folderset.add(path=sample_dir)
        return folderset

    return make