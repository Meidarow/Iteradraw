import logging
import sys

from PySide6 import QtWidgets

from iteradraw.container import DependencyContainer
from iteradraw.core.application.handlers.folder_handlers import \
    AddFolderCommandHandler, RemoveFolderCommandHandler, \
    RenameFolderSetCommandHandler, DeleteFolderSetCommandHandler, \
    AddFolderSetCommandHandler, SetFolderEnabledCommandHandler, \
    SetAllFoldersEnabledCommandHandler, \
    MoveFolderBetweenFolderSetsCommandHandler
from iteradraw.core.application.shell import ApplicationShell
from iteradraw.core.domain.repositories.folder_repository import \
    SQLite3FolderRepository
from iteradraw.core.infrastructure.buses.command_bus import CommandBus
from iteradraw.core.infrastructure.persistence.schema import SCHEMA
from iteradraw.core.infrastructure.persistence.sqlite3_database import \
    SQLite3Database
from iteradraw.core.infrastructure.persistence.unit_of_work import \
    SQLite3UnitOfWorkFactory
from iteradraw.interfaces import UnitOfWorkFactory, Database, FolderRepository
from iteradraw.log_config import configure_logger
from iteradraw.pyside.main_window import MainWindow
from iteradraw.pyside.pyside_shell import PySideShell

"""
Bootstrapper for Iteradraw app. 

Usage
-----
Run this file directly to start the app:
    python bootstrap.py
"""

ALL_HANDLERS = [
    AddFolderCommandHandler,
    RemoveFolderCommandHandler,
    RenameFolderSetCommandHandler,
    DeleteFolderSetCommandHandler,
    AddFolderSetCommandHandler,
    SetFolderEnabledCommandHandler,
    SetAllFoldersEnabledCommandHandler,
    MoveFolderBetweenFolderSetsCommandHandler,
]

logger = logging.getLogger("iteradraw.bootstrap")

def main() -> None:
    configure_logger()

    container = DependencyContainer()
    register_default_concrete_classes(container)

    database = container.resolve(SQLite3Database)
    initialize_detabase(database)

    command_bus = container.resolve(CommandBus)
    handler_instances = build_command_handlers(container)
    register_command_handlers(command_bus, handler_instances)

    shell = container.resolve(PySideShell)
    app = QtWidgets.QApplication(sys.argv)
    gui = MainWindow(shell=shell)
    gui.show()
    sys.exit(app.exec())


def initialize_detabase(database: Database) -> None:
    database.open()
    database.executescript(SCHEMA)
    database.commit()
    database.close()


def build_command_handlers(container: DependencyContainer) -> dict:
    handler_instances: dict = {}
    for handler_class in ALL_HANDLERS:
        handler_instances.setdefault(
            handler_class,
            container.resolve(handler_class))
    return handler_instances


def register_command_handlers(
        command_bus: CommandBus,
        handler_instances: dict
) -> None:
    for handler in handler_instances.values():
        command_bus.register(
            command_type=handler.command_type,
            handler=handler.handle,
        )

def register_default_concrete_classes(container: DependencyContainer) -> None:
    container.default_concretes[UnitOfWorkFactory] = SQLite3UnitOfWorkFactory
    container.default_concretes[ApplicationShell] = PySideShell
    container.default_concretes[FolderRepository] = SQLite3FolderRepository

if __name__ == "__main__":
    logger.info("Application started")
    main()
    logger.info("Application finished")
