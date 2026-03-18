from types import SimpleNamespace

import pytest

from iteradraw.bootstrap import ALL_HANDLERS, register_command_handlers
from iteradraw.core.application.shell import ApplicationShell
from iteradraw.core.infrastructure.buses.command_bus import CommandBus
from iteradraw.core.infrastructure.buses.event_bus import EventBus


@pytest.fixture(scope="function")
def mock_bootstrap(
        sqlite_database_in_memory,
        sqlite_folder_repo,
        sqlite_directory_repo,
        sqlite_unit_of_work_factory
) -> SimpleNamespace:
    command_bus = CommandBus()
    event_bus = EventBus()
    handler_instances = {}
    for handler_class in ALL_HANDLERS:
        handler_instances.setdefault(
            handler_class,
            handler_class(sqlite_unit_of_work_factory, event_bus)
        )
    register_command_handlers(command_bus, handler_instances)
    shell = ApplicationShell(
        command_bus=command_bus,
        event_bus=event_bus,
        uow_factory=sqlite_unit_of_work_factory
    )
    return SimpleNamespace(
        shell=shell,
        event_bus=event_bus,
        command_bus=command_bus,
        uow_factory=sqlite_unit_of_work_factory,
    )


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

        def test_add_folder_functionality(self, subtests, mock_bootstrap):
            app = mock_bootstrap
            with subtests.test("Empty folderset"):
                app.shell.add_folderset("Test Folderset")
            with subtests.test("Populated folderset"):
                ...

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
