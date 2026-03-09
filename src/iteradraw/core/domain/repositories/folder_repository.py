import sqlite3
from pathlib import Path

from iteradraw.core.domain.exceptions import PersistenceError, CommitError
from iteradraw.core.domain.models.folder import FolderSet, Folder
from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database
from iteradraw.interfaces import FolderRepository


class SQLFolderRepository(FolderRepository):

    DB_SCHEMA = """
    CREATE TABLE IF NOT EXISTS foldersets (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
        
    CREATE TABLE IF NOT EXISTS directories (
        dir_id INTEGER NOT NULL PRIMARY KEY,
        dir_name TEXT NOT NULL,
        crawl_time INT NOT NULL,
        mod_time INT NOT NULL, 
    );
        
    CREATE TABLE IF NOT EXISTS rootfolders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL,
        enabled BOOLEAN DEFAULT 1,
        folderset_id INT NOT NULL,
        UNIQUE (path, folderset_id),
        FOREIGN KEY(folderset_id) REFERENCES foldersets(id)
        ON DELETE CASCADE,
        FOREIGN KEY (id) REFERENCES directories(dir_id)
    );
        
    CREATE TABLE IF NOT EXISTS folders_closure (
        ancestor_id INT NOT NULL,
        descendant_id INT NOT NULL,
        depth INT NOT NULL,
        PRIMARY KEY (ancestor_id, descendant_id),
        FOREIGN KEY (ancestor_id) REFERENCES directories(dir_id),
        FOREIGN KEY (descendant_id) REFERENCES directories(dir_id)
    );
    """

    def __init__(
        self,
        database: SQLite3Database,
    ) -> None:
        self.database = database

    def initialize(self) -> None:
        """Configure database and ensure the schema exists."""
        self.database.open()
        self.database.execute("PRAGMA journal_mode = WAL;")
        self.database.execute("PRAGMA synchronous = NORMAL;")
        self.database.execute("PRAGMA temp_store = MEMORY;")
        self.database.execute("PRAGMA foreign_keys = ON;")
        self.database.executescript(self.DB_SCHEMA)
        self.database.row_factory = sqlite3.Row

    def get_all_foldersets(self) -> list[FolderSet]:
        """
        Retrieves all FolderSets from the DB and reconstructs them.
        """
        query = """
        SELECT fs.id, fs.name, f.path, f.enabled FROM foldersets fs
        LEFT JOIN rootfolders f ON f.folderset_id = fs.id ORDER BY fs.id;
        """
        foldersets_map = {}

        for row in self.database.execute(query).fetchall():
            if row["id"] not in foldersets_map:
                foldersets_map[row["id"]] = {
                    "name": row["name"],
                    "folders": {},
                }
            if not row["path"]:
                continue
            foldersets_map[row["id"]]["folders"][Path(row["path"])] = Folder(
                path=Path(row["path"]), enabled=row["enabled"]
            )

        return [FolderSet(
                id=folderset_id,
                display_name=data["name"],
                folders=data["folders"],
            ) for folderset_id, data in foldersets_map.items()]

    def save_folderset(self, folderset: FolderSet):
        """
        Saves a FolderSet aggregate to the DB in a transaction.
        """
        try:
            with self.database:
                self._upsert_foldersets(folderset)
                root_folder_list = [str(folder) for folder in folderset.folders.keys()]
                inserted_directory_id_list = self._insert_directories(root_folder_list)
                self._insert_closure_nodes(inserted_directory_id_list)
                folderset_data =[(str(f.path), f.enabled, folderset.id) for f in folderset.all]
                self._insert_root_folders(folderset_data)
                self._prune_root_folders(root_folder_list, folderset.id)
                self._prune_directories()
        except sqlite3.DatabaseError as e:
            raise PersistenceError("Failed to save folderset") from e

    def register_folderset(self, folderset_name: str) -> int:
        try:
            with self.database:
                cursor = self.database.execute(
                    """
                    INSERT INTO foldersets VALUES (?) RETURNING id;
                    """,
                    (folderset_name,),
                )
                return cursor.fetchone()["id"]
        except sqlite3.DatabaseError as e:
            raise PersistenceError("Failed to add folderset") from e

    def delete_folderset(self, folderset_id: int) -> None:
        try:
            with self.database:
                self.database.execute(
                    "DELETE FROM foldersets WHERE id = ?",
                    (folderset_id,),
                )
                self._prune_directories()
        except sqlite3.DatabaseError as e:
            raise PersistenceError("Failed to delete folderset") from e

    ### Crawl relevant

    def add_discovered_folder(self):
        #todo
        ...


    def fetch_directories(self) -> list[Folder]:
        query = """
        SELECT dir_id from directories WHERE crawl_time < mod_time OR crawl_time = 0
        """


    # Private Helpers:


    def _insert_directories(self, root_folders: list[str]) ->list[int]:
        dir_id_list = []
        if root_folders:
            insert_folders_query = " ".join(
                ["INSERT INTO directories (dir_name, crawl_time, mod_time) VALUES",
                 ", ".join(["(?, 0, 0)" for _ in range(len(root_folders))]),
                "ON CONFLICT (dir_name) DO UPDATE SET crawl_time = crawl_time RETURNING dir_id"]
            )
            rows = self.database.execute(insert_folders_query, root_folders).fetchall()
            dir_id_list = [(directory_id["dir_id"]) for directory_id in rows]
        return dir_id_list

    def _prune_directories(self) -> None:
        self.database.execute(
            """
            DELETE FROM directories WHERE dir_id NOT IN (
            SELECT descendant_id FROM folders_closure WHERE ancestor_id IN (
            SELECT id FROM rootfolders))
            """
        )

    def _insert_closure_nodes(self, dir_id_list: list[int]) -> None:
        if dir_id_list:
            directory_data = [(directory_id, directory_id) for directory_id in dir_id_list]
            self.database.executemany(
                """
                INSERT INTO folders_closure (ancestor_id, descendant_id, depth)
                VALUES (?, ?, 0)
                """,
                directory_data)

    def _upsert_foldersets(self, folderset: FolderSet) -> None:
        self.database.execute(
            """
            INSERT INTO foldersets (id, name) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET name=excluded.name
            RETURNING id
            """,
            (folderset.id, folderset.display_name),
        )

    def _insert_root_folders(self, root_folder_data: list[tuple[str, bool, int]]) -> None:
        if root_folder_data:
            self.database.executemany(
                """
                INSERT INTO rootfolders (path, enabled, folderset_id)
                VALUES (?, ?, ?)
                ON CONFLICT (path, folderset_id) DO NOTHING
                """,
                root_folder_data,
            )

    def _prune_root_folders(self, root_folders: list[str], folderset_id: int) -> None:
        params = [folderset_id , *root_folders]
        self.database.execute(
            " ".join([f"DELETE FROM rootfolders WHERE folderset_id = ? AND path NOT IN",
            "(", ", ".join(["?" for _ in range(len(root_folders))]), ")"]),
            params,
        )