from pathlib import Path

import pytest

from iteradraw.core.domain.models.folder import FolderSet


class TestFolderSetModel:
    class TestRemove:
        def test_remove_existing_folder(self):
            folderset = FolderSet(
                id=2,
                display_name="Test Folder Set"
            )
            folderset = folderset.add(Path("fake/folder/foo/bar.png"), True)
            folderset = folderset.remove(Path("fake/folder/foo/bar.png"))
            assert folderset.folders == {}

        def test_remove_nonexisting_folder(self):
            folderset = FolderSet(
                id=2,
                display_name="Test Folder Set"
            )
            with pytest.raises(KeyError):
                folderset.remove(Path("fake/folder/foo/bar.png"))

        def test_remove_invalid_path_type(self):
            folderset = FolderSet(
                id=2,
                display_name="Test Folder Set"
            )
            folderset = folderset.add(Path("fake/folder/foo/bar.png"), True)
            with pytest.raises(TypeError):
                folderset.remove("fake/folder/foo/bar.png")

    class TestAdd:
        ...
    class TestRename:
        ...
    class TestFolderEnable:
        ...
    class TestAllFolderEnable:
        ...