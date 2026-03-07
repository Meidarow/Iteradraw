from abc import ABC
from os import PathLike
from typing import runtime_checkable, Protocol, Iterator, Iterable, Any, Type, TypeVar, Generic
from uuid import UUID

from iteradraw.core.domain.models.folder import FolderSet


class Command(Protocol):
    ...


TCommand = TypeVar("TCommand", bound="Command")

class CommandHandler(ABC, Generic[TCommand]):
    command_type : Type[TCommand]
    def handle(self, command: TCommand):
        ...

class Event(Protocol):
    ...

class ICache(ABC):
    def get(self): ...
    def put(self): ...

@runtime_checkable
class IdGenerator(Protocol):
    def generate(self) -> UUID:
        ...

@runtime_checkable
class StatLike(Protocol):
    st_mtime: float
    st_ino: int
    st_dev: int


@runtime_checkable
class DirEntryLike(Protocol):
    path: str

    def is_dir(self) -> bool:
        ...

    def is_symlink(self) -> bool:
        ...

    def stat(self) -> "StatLike":
        ...


@runtime_checkable
class FilterLike(Protocol):
    def add(self, item: str) -> None:
        ...

    def __contains__(self, item: str) -> bool:
        ...


@runtime_checkable
class DirectoryScanner(Protocol):
    def __call__(self, directory: PathLike) -> Iterator["DirEntryLike"]:
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


class FolderRepository(Protocol):
    """
    Repository for FolderSet domain objects.
    """

    def __init__(self, persistence):
        ...

    def get(self, folderset_id: UUID) -> FolderSet:
        ...

    def get_all(self) -> list[FolderSet]:
        ...

    def save(self, folderset: FolderSet):
        ...

    def remove(self, folderset_id: UUID):
        ...



class SessionRepository(Protocol):
    """Abstract interface for database backends used in Draw-This."""

    def initialize(self) -> None:
        """Establish a connection and prepare for access."""

    def clear_all(self) -> None:
        """Remove all rows from the database (reset state)."""

    def setup_schema(self) -> None:
        """Initialize database schema if not already created."""

    def insert_rows(self, rows: Iterable[tuple]) -> int:
        """
        Insert multiple rows into the database.

        Args:
            rows: An iterable of row tuples matching schema.
        Returns:
            int: Number of rows successfully inserted.
        """

    def remove_rows(self, paths: Iterable[str]) -> int:
        """
        Remove rows that match given file paths.

        Args:
            paths: Iterable of file paths to delete.
        Returns:
            int: Number of rows removed.
        """

    def mark_seen(self, ids: Iterable[Any], seen: bool = True) -> int:
        """
        Update the 'seen' status of rows.

        Args:
            ids: Iterable of row IDs.
            seen: New seen status (default True).
        Returns:
            int: Number of rows updated.
        """

    def shuffle(self) -> None:
        """
        Apply randomization strategy (if supported).
        For SQLite this might reorder rows, for other backends it may differ.
        """


class PreferencesPersistence(Protocol):
    """
    Persistence protocol for domain objects, intended for user-preferences
    and content.

    Defines API that must be public in concrete implementations for
    hot-swappale backends to properly be consumed by the repository layer.
    """

    def read_file(self):
        """
        Decodes file
        """

    def write_file(self, namespace):
        """
        Encodes file
        """
