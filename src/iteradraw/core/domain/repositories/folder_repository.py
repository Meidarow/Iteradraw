import logging
import sqlite3
from pathlib import Path

from iteradraw.core.domain.exceptions import PersistenceError
from iteradraw.core.domain.models.folder import FolderSet, Folder
from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database
from iteradraw.interfaces import FolderRepository

logger = logging.getLogger(__name__)

class SQLite3FolderRepository(FolderRepository):
    """
    Repository class managing UI facing data.

    Tables:
        - foldersets: FolderSet aggregates.
        - rootfolders: User added folders and their metadata.
    """

    def __init__(
        self,
        database: SQLite3Database,
    ) -> None:
        self.database = database

    def get_foldersets(self) -> list[FolderSet]:
        """
        Retrieves all FolderSet data from the database and returns FolderSet
        objects with them.
        """
        query = """
        SELECT fs.id, fs.name, f.path, f.enabled FROM foldersets fs
        LEFT JOIN rootfolders f ON f.folderset_id = fs.id ORDER BY fs.id;
        """
        foldersets_map = {}

        for row in self.database.execute(query).fetchall():
            foldersets_map.setdefault(row["id"], {
                "name": row["name"],
                "folders": {},
            })
            if not row["path"]:
                continue
            foldersets_map[row["id"]]["folders"][Path(row["path"])] = Folder(
                path=Path(row["path"]),
                enabled=row["enabled"]
            )

        return [FolderSet(
                id=folderset_id,
                display_name=data["name"],
                folders=data["folders"],
            ) for folderset_id, data in foldersets_map.items()]

    def create_folderset(self, folderset_name: str) -> int:
        """
        Creates a new folderset in the DB.

        Returns:
            int: Unique id of the new folderset.
        Raises:
            PersistenceError: Error when creating folderset.
        """
        query = """
        INSERT INTO foldersets (name) VALUES (?) RETURNING id;
        """
        try:
            cursor = self.database.execute(query,(folderset_name,),)
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error when creating folderset") from e

        return cursor.fetchone()["id"]

    def delete_folderset(self, folderset_id: int) -> None:
        """
        Deletes a folderset from the DB.

        Raises:
            PersistenceError: Error when deleting folderset.
        """
        query = "DELETE FROM foldersets WHERE id = ?"
        try:
            self.database.execute(query,(folderset_id,),)
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error when deleting folderset") from e

    def update_folderset_folders(self, folderset: FolderSet) -> None:
        """
        Updates a FolderSet's folders in the DB.
        """
        folderset_data: list[tuple[str, bool, int]] = []
        root_folders: list[str] = []
        for f in folderset.all:
            root_folders.append(str(f.path))
            folderset_data.append((str(f.path), f.enabled, folderset.id))

        self._insert_root_folders(folderset_data)
        self._prune_root_folders(root_folders, folderset.id)


    def update_folderset_name(self, folderset: FolderSet) -> None:
        """
        Updates folderset name in the DB.

        Raises:
            PersistenceError: Failed to update folderset name.
                              Error when updating folderset name.
        """
        query = """UPDATE foldersets  SET name = (?) WHERE id = ?"""
        try:
            cursor = self.database.execute(
                query,(folderset.display_name, folderset.id),
            )
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error when updating folderset name") from e

        if cursor.rowcount != 1:
            logger.warning(f"{cursor.rowcount} row(s) affected.")
            raise PersistenceError("Failed to update folderset name")

    # Private Helpers:

    def _insert_root_folders(self, root_folder_data: list[tuple[str, bool, int]]) -> None:
        """
        Inserts the root folders in the DB.

        Args:
            root_folder_data: Path, enabled status and owner folderset ID.
        Raises:
            PersistenceError: Error when inserting root folders.
                              Directories node does not exist.
        """
        if not root_folder_data:
            return
        query = """
        INSERT INTO rootfolders (path, enabled, folderset_id)
        VALUES (?, ?, ?)
        ON CONFLICT (path, folderset_id) DO NOTHING
        """
        try:
            self.database.executemany(query,root_folder_data,)
        except sqlite3.IntegrityError:
            logger.error("Directory node missing from directories table",
                         exc_info=True)
            raise PersistenceError("Directories node does not exist") from None
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error when inserting root folders") from e

    def _prune_root_folders(self, root_folders: list[str], folderset_id: int
                            ) -> None:
        """
        Removes folders that are not in "root_folders" from the DB.

        Args:
            root_folders: Folders to be kept in the DB.
            folderset_id: ID of the folderset to be pruned.
        Raises:
            PersistenceError: Error when pruning root folders.
        """
        if not root_folders:
            query = """DELETE FROM rootfolders WHERE folderset_id = ?"""
        else:
            query = " ".join(
                [f"DELETE FROM rootfolders WHERE folderset_id = ? AND path NOT IN",
                 "(", ", ".join(["?" for _ in range(len(root_folders))]), ")"])
        params: list[int | str] = [folderset_id, *root_folders]
        try:
            self.database.execute(query,params,)
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error when pruning root folders") from e