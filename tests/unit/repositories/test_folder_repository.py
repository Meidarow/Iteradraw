"""
Test suite for SQLFolderRepository
"""
from pathlib import Path

import pytest

from iteradraw.core.domain.exceptions import PersistenceError


class TestCreateFolderset:
    def test_create_folderset(self, sqlite_unit_of_work):
        fs_name = "Test Folder Set"
        with sqlite_unit_of_work as uow:
            fs_id = uow.folder_repo.create_folderset(fs_name)
            db_fs = uow.database.execute(
                "SELECT * FROM foldersets WHERE id = ?",
                                 (fs_id,)).fetchone()
            uow.commit()
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

    def test_update_folderset_name(self, sqlite_unit_of_work,
                                   make_mock_folderset):
        folderset = make_mock_folderset(name="OLD NAME")
        folderset = folderset.rename("NEW NAME")

        with sqlite_unit_of_work as uow:
            uow.folder_repo.update_folderset_name(folderset)
            folderset = uow.folder_repo.get_foldersets().pop()
            uow.commit()

        assert folderset.display_name == "NEW NAME"

    def test_update_folderset_folder_add(self, sqlite_unit_of_work,
                                         make_mock_folderset):
        folderset = make_mock_folderset(dir_number=1)
        folder = list(folderset.folders.keys()).pop()

        with sqlite_unit_of_work as uow:
            uow.folder_repo.update_folderset_folders(folderset)
            folderset = uow.folder_repo.get_foldersets().pop()
            uow.commit()

        directory = list(folderset.folders.keys()).pop()
        assert directory == folder

    def test_update_folderset_add_missing_directory(self, sqlite_unit_of_work,
                                                    make_mock_folderset):
        folderset = make_mock_folderset()
        sample_dir = Path('/path/not/in/directories/database')
        folderset = folderset.add(sample_dir, True)
        with sqlite_unit_of_work as uow:
            with pytest.raises(PersistenceError):
                uow.folder_repo.update_folderset_folders(folderset)

    def test_update_folderset_folder_remove(self, sqlite_unit_of_work,
                                            make_mock_folderset):
        folderset_pre = make_mock_folderset(dir_number=1)
        with sqlite_unit_of_work as uow:
            uow.folder_repo.update_folderset_folders(folderset_pre)
            folder = folderset_pre.all.pop().path

            folderset_post = folderset_pre.remove(folder)
            uow.folder_repo.update_folderset_folders(folderset_post)

            folderset_db = uow.folder_repo.get_foldersets().pop()
        assert folder not in folderset_db.folders


class TestRemoveFolderset:
    def test_folderset_remove(self, make_mock_folderset): ...
