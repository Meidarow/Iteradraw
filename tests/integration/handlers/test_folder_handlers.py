from pathlib import Path
from typing import Type

import pytest

from iteradraw.core.application.commands.folder_commands import AddFolderCommand
from iteradraw.core.application.handlers.folder_handlers import \
    AddFolderCommandHandler
from iteradraw.interfaces import CommandHandler


class TestFolderHandlers:
    @pytest.fixture(scope="function")
    def mock_handler(self, mock_event_bus, sqlite_unit_of_work_factory):
        def handler(handler_cls: Type[CommandHandler]):
            return handler_cls(
                sqlite_unit_of_work_factory,
                mock_event_bus,
            )

        return handler

    class TestAddFolderCommandHandler:
        def test_add_folder_handler_functionality(
                self,
                mock_event_bus,
                mock_handler,
                make_mock_folderset
        ):
            folderset = make_mock_folderset()
            handler = mock_handler(AddFolderCommandHandler)
            for i in range(10):
                command = AddFolderCommand(
                    folderset_id=folderset.id,
                    folder_path=Path(f"/foo/bar/baz/folder_path_{i}"),
                    enabled=True,
                )
                handler.handle(command)
                assert True


    class TestRemoveFolderCommandHandler:
        ...

    class TestRenameFolderSetCommandHandler:
        ...

    class TestAddFolderSetCommandHandler:
        ...

    class TestDeleteFolderSetCommandHandler:
        ...

    class TestSetFolderEnabledCommandHandler:
        ...

    class TestSetAllFoldersEnabledCommandHandler:
        ...

    class TestMoveFolderBetweenFolderSetsCommandHandler:
        ...
