import logging

from iteradraw.container import DependencyContainer
from iteradraw.core.domain.repositories.directory_repository import \
    SQLite3DirectoryRepository
from iteradraw.core.domain.repositories.folder_repository import \
    SQLite3FolderRepository
from iteradraw.core.domain.repositories.image_repository import SQLImageRepository
from iteradraw.core.infrastructure.buses.command_bus import CommandBus
from iteradraw.core.infrastructure.persistence.schema import SCHEMA
from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database
from iteradraw.core.infrastructure.persistence.unit_of_work import \
    SQLite3UnitOfWorkFactory
from iteradraw.interfaces import CommandHandler, FolderRepository, \
    ImageRepository, DirectoryRepository, UnitOfWorkFactory
from iteradraw.log_config import configure_logger

"""
Bootstrapper for Iteradraw app. 

Usage
-----
Run this file directly to start the app:
    python bootstrap.py
"""

logger = logging.getLogger("iteradraw.bootstrap")

def main() -> None:
    configure_logger()
    container = DependencyContainer()
    register_default_concrete_classes(container)
    database = container.resolve(SQLite3Database)
    database.open()
    database.executescript(SCHEMA)
    database.close()
    build_command_pipeline(container)

def build_command_pipeline(container: DependencyContainer) -> None:
    command_bus = container.resolve(CommandBus)
    for handler_class in CommandHandler.__subclasses__():
        handler = container.resolve(handler_class)
        command_bus.register(
            command_type=handler.command_type,
            handler=handler.handle,
        )

def register_default_concrete_classes(container: DependencyContainer) -> None:
    container.default_concretes[UnitOfWorkFactory]=SQLite3UnitOfWorkFactory

if __name__ == "__main__":
    logger.info("Application started")
    main()
    logger.info("Application finished")
