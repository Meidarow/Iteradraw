"""
Test suite for SQLFolderRepository
"""
from pathlib import Path

import pytest

from iteradraw.core.domain.exceptions import PersistenceError


class TestCreateFolderset:
    def test_create_folderset(self, setup):
        fs_name = "Test Folder Set"
        fs_id = setup.repository.create_folderset(fs_name)
        db_fs = setup.db.execute("SELECT * FROM foldersets WHERE id = ?",
                                 (fs_id,)).fetchone()
        assert fs_id == db_fs["id"]
        assert fs_name == db_fs["name"]

class TestGetFoldersets:
    ...

class TestUpdateFolderset:
    """
    Behavioral contract for folderset updates

    Assumptions:
    - A folderset with valid ID exists in the database
    - Paths to folders are valid directories
    - Path to folder is absolute path with '..' and symlinks resolved

    Compromises:
    - A folder shared by foldersets must have shared enabled status

    Expected behavior (how it should do things):
    - Multiple foldersets may contain the same folder
    - Deleting one of multiple instances of a folder in foldersets does not remove the directory node
    - A folderset may not contain duplicates of the same folders

    Acceptance criteria (what it does/returns):
    -

    """
    def test_update_folderset_name(self, setup, make_folderset):
        folderset = make_folderset(name="OLD NAME")
        folderset = folderset.rename("NEW NAME")
        setup.repository.update_folderset_name(folderset)

        folderset = setup.repository.get_foldersets().pop()
        assert folderset.display_name == "NEW NAME"

    def test_update_folderset_folder_add(self, setup, make_folderset):
        folderset = make_folderset(dir_number=1)
        folder = list(folderset.folders.keys()).pop()

        setup.repository.update_folderset_folders(folderset)
        folderset = setup.repository.get_foldersets().pop()

        directory = list(folderset.folders.keys()).pop()
        assert directory == folder

    def test_update_folderset_add_missing_directory(self, setup,
                                                    make_folderset):
        folderset = make_folderset()
        sample_dir = Path('/path/not/in/directories/database')
        folderset = folderset.add(sample_dir, True)
        with pytest.raises(PersistenceError):
            setup.repository.update_folderset_folders(folderset)

    def test_update_folderset_folder_remove(self, setup, make_folderset):
        folderset_pre = make_folderset(dir_number=1)
        setup.repository.update_folderset_folders(folderset_pre)
        folder = folderset_pre.all.pop().path

        folderset_post = folderset_pre.remove(folder)
        setup.repository.update_folderset_folders(folderset_post)

        folderset_db = setup.repository.get_foldersets().pop()
        assert folder not in folderset_db.folders


class TestRemoveFolderset:
    def test_folderset_remove(self, setup, make_folderset):...
