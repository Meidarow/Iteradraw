from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import runtime_checkable, Protocol, Iterator, Iterable, Any, Type, TypeVar, Generic
from uuid import UUID

from iteradraw.core.domain.models.folder import FolderSet


class Event(ABC):
    ...

class Command(ABC):
    ...

TCommand = TypeVar("TCommand", bound="Command")

class CommandHandler(ABC, Generic[TCommand]):
    command_type : Type[TCommand]
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

Usage:

"""


class FolderRepository(ABC):
    """
    Repository for FolderSet domain objects.
    """
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
    def __call__(self):
        ...

class UnitOfWork(ABC):
    @abstractmethod
    def __enter__(self):
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    @abstractmethod
    def commit(self):
        ...

    @abstractmethod
    def rollback(self):
        ...