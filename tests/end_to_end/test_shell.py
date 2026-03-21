from iteradraw.core.domain.events.folder_events import FolderSetCreated

class TestApplicationShell:
    class TestRenameFolderset:
        def test_single_folderset_rename(self): ...

        def test_invalid_folderset_rename(self): ...

        def test_multiple_folderset_rename(self): ...

        def test_duplicate_name_folderset_rename(self): ...

    class TestAddFolderset:
        def test_add_folderset(self, subtests, mock_bootstrap):
            app = mock_bootstrap
            with subtests.test("No foldersets"):
                app.shell.add_folderset("Test Folderset")
                with app.uow_factory() as uow:
                    foldersets = uow.folder_repo.get_foldersets()
                    assert foldersets[0].display_name == "Test Folderset"

            with subtests.test("Existing foldersets"):
                app.shell.add_folderset("Test Folderset 2")
                with app.uow_factory() as uow:
                    foldersets = uow.folder_repo.get_foldersets()
                    assert foldersets[1].display_name == "Test Folderset 2"

        def test_multiple_foldersets_add_folderset(self): ...

        def test_duplicate_name_foldersets_add_folderset(self): ...

    class TestDeleteFolderset:
        ...

    class TestAddFolder:
        """
        ApplicationShell add_folder behavioral contract:

        Expected behavior:
            - Folders may be referenced by multiple foldersets and must share
              same enabled status across foldersets.
            - A given folderset may not possess duplicate folders.

        Acceptance criteria:
            - Adding duplicate folders to a folderset is rejected.
            - Adding one folder to multiple foldersets is allowed.
            - All duplicate folders share same enabled status.
        """

        def test_add_folder_functionality(self, mock_bootstrap):
            app = mock_bootstrap
            test: dict[str, int] = {}

            def set_id(x):
                test["id"] = x

            app.event_bus.subscribe(
                FolderSetCreated,
                (lambda x: set_id(x.folderset_id)), )
            app.shell.add_folderset("Test Folderset")
            for i in range(10):
                app.shell.add_folder(test["id"], "/Test/Folder/%i" % i)


        def test_invalid_folderset_add_folder(self): ...

    class TestRemoveFolder:
        """
        ApplicationShell remove_folder behavioral contract:

        Expected behavior:
            - A folder must be valid as long as at least one folderset holds it.
        """

        def test_empty_folderset_remove_folder(self): ...

        def test_single_folder_folderset_remove_folder(self): ...

        def test_multiple_folder_folderset_remove_folder(self): ...

        def test_invalid_folderset_remove_folder(self): ...

    class TestSetFoldersetEnabled:
        ...

    class TestSetAllFoldersEnabled:
        ...

    class TestMoveFolder:
        ...

    class TestStart:
        ...

    class TestShutdown:
        ...

    class TestNextTimedSlide:
        ...

    class TestPreviousTimedSlide:
        ...

    class TestNextSlide:
        ...

    class TestPreviousSlide:
        ...

    class TestFetchFolderset:
        ...

    class TestFetchSessionStatistics:
        ...

    class TestFetchSessionImages:
        ...

    class TestFetchTags:
        ...
