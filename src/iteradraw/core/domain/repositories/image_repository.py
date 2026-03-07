from typing import Callable

from iteradraw.core.domain.models.timer import TimerSet


class TimerRepository:
    """
    Repository for TimerSet domain objects.

    Facilitates persistence operations for the TimerSet model by
    abstracting backend implementations and providing (de-)serialization
    methods. Allows for backend injection, as long as implementation
    follows the Persistence protocol.
    """

    DB_SCHEMA = """
    CREATE TABLE IF NOT EXISTS images (
        image_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        parent_dir INTEGER NOT NULL,
        FOREIGN KEY (parent_dir) REFERENCES discovered_folders(dir_id)
        ON DELETE CASCADE
    );
    """

    def __init__(
        self, persistence: Persistence, platform_config_dir: Callable
    ):
        self.persistence = persistence or JsonPersistence(
            namespace=RepositoryNamespaces.Timers,
            file_name="session.json",
            settings_dir_path=platform_config_dir(),
            on_read_error=None,
            on_write_error=None,
        )

    def get_all(self) -> list[TimerSet]: ...

    def save(self, data: list[TimerSet]): ...

    @staticmethod
    def _from_list(timers: list[int]) -> TimerSet:
        """Factory for TimerSet from list of timers"""
        ts = TimerSet()
        for timer in timers:
            ts.add(timer)
        return ts
