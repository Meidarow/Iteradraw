from types import SimpleNamespace

import pytest

from iteradraw.core.domain.models.folder import FolderSet


@pytest.fixture(scope="function")
def setup(sqlite_database_in_memory, sqlite_folder_repo):
    return SimpleNamespace(
        db=sqlite_database_in_memory,
        repository=sqlite_folder_repo)

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