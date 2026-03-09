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
class DirectoryScanner(Protocol):
    def __call__(self, directory: PathLike) -> Iterator[Any]:
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
    def get(self, folderset_id: int) -> FolderSet:
        ...

    def register_folderset(self, folderset_name: str) -> int:
        ...

    def get_all(self) -> list[FolderSet]:
        ...

    def save(self, folderset: FolderSet):
        ...

    def remove(self, folderset_id: int):
        ...



class SessionRepository(Protocol):
    """Abstract interface for database backends used in Draw-This."""

    def initialize(self) -> None:
        """Establish a connection and prepare for access."""

    def setup_schema(self) -> None:
        """Initialize database schema if not already created."""


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
