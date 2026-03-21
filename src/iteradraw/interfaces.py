from __future__ import annotations

import typing
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Any, Type, TypeVar, Generic

if typing.TYPE_CHECKING:
    from iteradraw.core.domain.models.folder import FolderSet
    from iteradraw.core.infrastructure.buses.event_bus import EventBus


class Event(ABC):
    ...

class Command(ABC):
    ...

TCommand = TypeVar("TCommand", bound="Command")

class CommandHandler(ABC, Generic[TCommand]):
    command_type : Type[TCommand]

    @abstractmethod
    def __init__(
            self,
            unit_of_work_factory: UnitOfWorkFactory,
            event_bus: EventBus
    ) -> None:
        ...

    def handle(self, command: TCommand):
        ...

"""
Interface protocols for the persistence layer of Iteradraw.

This module defines protocols that apply generically and universally to all 
backend implementations meant for persistence, with the intention of 
simplifying persistence operations, encapsulating persistence domain 
knowledge to its layer and allowing hot-swapping of backends

Iteradraw uses persistence in two ways: settings and session storage for 
user-preferences and content, and for resource management during slideshow 
sessions. 

Classes:
    DatabaseBackend: protocol for session resource management backends.
    Persistence: protocol for settings/user-prefs/content backends.
"""


class Database(ABC):
    @abstractmethod
    def __enter__(self) -> Database:
        ...

    @abstractmethod
    def execute(self, query, params):
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...


class FolderRepository(ABC):
    """
    Repository for FolderSet domain objects.
    """

    @abstractmethod
    def get_folderset(self, folderset_id: int) -> FolderSet:
        ...

    @abstractmethod
    def get_foldersets(self) -> list[FolderSet]:
        ...

    @abstractmethod
    def update_folderset_name(self, folderset: FolderSet) -> None:
        ...

    @abstractmethod
    def update_folderset_folders(self, folderset: FolderSet) -> None:
        ...

    @abstractmethod
    def create_folderset(self, folderset_name: str) -> int:
        ...

    @abstractmethod
    def delete_folderset(self, folderset_id: int) -> None:
        ...


class DirectoryRepository(ABC):
    """
    Repository for directories for filesystem operations.
    """
    @abstractmethod
    def create_directory(self, dir_name: str, parent_id: int,
                         crawl_time: int, mod_time: int) -> int:
        ...

    @abstractmethod
    def get_directories(self) -> dict[int, dict[str, str | int | set | bool]]:
        ...

    @abstractmethod
    def get_normalized_path(self, dir_id: int) -> Path:
        ...

    @abstractmethod
    def update_directory(self, dir_id: int, crawl_time: int = 0,
                         mod_time: int = 0) -> None:
        ...

    @abstractmethod
    def create_directories(self, dirs: list[Path]) -> list[int]:
        ...

    @abstractmethod
    def is_duplicate(self, dir_path: Path) -> int | None:
        ...


class ImageRepository(ABC):
    """Repository of images"""
    @abstractmethod
    def insert_image_batch(self, batch: Iterable[Any]) -> None:
        ...

    @abstractmethod
    def clear_images_under_parent(self, parent_id: int) -> None:
        ...


class SessionRepository(ABC):
    """Abstract interface for database backends used in Draw-This."""
    ...


class UnitOfWorkFactory(ABC):
    @abstractmethod
    def __call__(self) -> UnitOfWork:
        ...


class UnitOfWork(ABC):
    dir_repo: DirectoryRepository
    folder_repo : FolderRepository
    database : Database

    @abstractmethod
    def __enter__(self) -> UnitOfWork:
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    @abstractmethod
    def commit(self)-> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...