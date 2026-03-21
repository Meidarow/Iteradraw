import logging
import os
import random
import time
from os import DirEntry
from typing import Generator

from iteradraw.interfaces import DirectoryRepository, ImageRepository

"""

"""

logger = logging.getLogger(__name__)

class FileDiscoveryService:
    """
    Service class responsible for filesystem traversal and DB tree maintenance.
    """

    class _Crawler:
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
            self.files_skipped = 0

        def crawl(self, folder: str) -> Generator[DirEntry]:
            """Yield os.DirEntry objects for every file found in folders."""
            try:
                for entry in os.scandir(folder):
                    if entry.is_symlink():
                        continue
                    yield entry
            except (
                    PermissionError,
                    FileNotFoundError,
                    NotADirectoryError,
            ):
                self.files_skipped += 1
                logger.debug(
                    f"Skipped {folder}", exc_info=True
                )

    def __init__(
        self,
        dir_repo: DirectoryRepository,
        image_repo: ImageRepository
    ):
        self._fresh_dirs = set()
        self._stale_dirs = set()
        self.dir_repo = dir_repo
        self.image_repo = image_repo
        self.crawler = self._Crawler()

    def scan_stale_directories(self):
        self._sort_directories(self.dir_repo.get_directories())
        batch = []
        while self._stale_dirs:
            stale_dir_id, stale_dir_path = self._stale_dirs.pop()
            generator = self.crawler.crawl(stale_dir_path)
            crawl_time = int(time.time())
            mod_time = int(os.stat(stale_dir_path).st_mtime)
            self.dir_repo.update_directory(
                dir_id=stale_dir_id,
                crawl_time=crawl_time,
                mod_time=mod_time,
            )
            for entry in generator:
                if entry.is_dir() and entry.path not in self._fresh_dirs:
                    dir_id = self.dir_repo.create_directory(
                        dir_name=entry.name,
                        crawl_time=0,
                        mod_time=0,
                        parent_id=stale_dir_id
                    )
                    self._stale_dirs.add((dir_id, entry.path))
                    self._fresh_dirs.add(entry.path)
                else:
                    row = (entry.name, stale_dir_id)
                    batch.append(row)
                    # if len(batch) == 5000:
                    #     random.shuffle(batch)
                    #     self.image_repo.insert_image_batch(batch)
                    #     batch.clear()
        random.shuffle(batch)
        self.image_repo.insert_image_batch(batch)
        self._fresh_dirs.clear()

    def _sort_directories(self, directories) -> None:
        for dir_id, dir_data in directories.items():
            if dir_data["crawl_time"] < dir_data["mod_time"] or dir_data[
                "crawl_time"] == 0:
                self._stale_dirs.add((dir_id, dir_data["path"]))
            else:
                self._fresh_dirs.add(dir_data["path"])
