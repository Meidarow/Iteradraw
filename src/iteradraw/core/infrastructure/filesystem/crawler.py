import logging
import os
import random
from pathlib import Path
from typing import (
    Iterable,
    Generator,
)

logger = logging.getLogger(__name__)

class Crawler:
    """
    Walks directories recursively and yields DirEntry objects.
    Guarantees:
    - Duplicate safe (Visited set)
    - Recursion safe (symlinks handled)
    - Skips inaccessible files gracefully

    Notes:
        -Converts DirEntryLike objects into static FileEntry objects
        -Use as a context manager for automatic cleanup, or manage cleanup
         manually via clear_queue() / reset_state() for long-lived crawlers.
    """

    def __init__(self):
        self.directory_set: set[Path] = set()
        self._files_skipped = 0
        self.visited = set()

    def __enter__(self):
        self.reset_state()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset_state()

    def reset_state(self):
        """Reset Crawler for re-use, also resets skipped files counter"""
        self._files_skipped = 0
        self.directory_set.clear()
        self.visited = set()

    def crawl(self, folders) -> Iterable[os.DirEntry]:
        """Yield os.DirEntry objects for every file found in folders."""
        self._enqueue(folders)

        while self.directory_set:
            current_directory = random.sample(self.directory_set, 1)[0]
            self.directory_set.discard(current_directory)
            self.visited.add(current_directory)
            try:
                yield from self._generate_entries_from(current_directory)
            except (
                PermissionError,
                FileNotFoundError,
                NotADirectoryError,
            ):
                self._files_skipped += 1
                logger.debug(
                    f"Skipped {current_directory}", exc_info=True
                )

    # Accessors for internal metrics

    @property
    def files_skipped(self):
        return self._files_skipped

    # Private Helpers

    def _generate_entries_from(
        self, directory: Path
    ) -> Generator[os.DirEntry, None, None]:
        for entry in os.scandir(str(directory)):
            if entry.is_symlink():
                # skip
                continue

            if entry.is_dir():
                # store absolute path for recursion safety
                self._enqueue((Path(entry.path),))
                continue

            yield entry

    def _enqueue(self, folders: Iterable[Path]) -> None:
        """Add folders to Crawler's queue"""
        for directory in folders:
            try:
                absolute_path = Path(directory).absolute()
                if absolute_path in self.visited:
                    logger.debug("Recursion skipped")
                    continue
                self.directory_set.add(absolute_path)
            except OSError:  # e.g. broken link
                logger.warning("Relative to absolute path conversion failed", exc_info=True)
