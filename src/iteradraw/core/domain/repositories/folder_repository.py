import sqlite3
from pathlib import Path

from iteradraw.core.domain.exceptions import PersistenceError
from iteradraw.core.domain.models.folder import FolderSet, Folder
from iteradraw.core.infrastructure.persistence.sqlite3_database import SQLite3Database
from iteradraw.interfaces import FolderRepository, DirectoryRepository


class SQLFoldersetRepository(FolderRepository):

    def __init__(
        self,
        database: SQLite3Database,
    ) -> None:
        self.database = database

    def get_foldersets(self) -> list[FolderSet]:
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

    def update_folderset(self, folderset: FolderSet) -> None:
        """
        Updates a FolderSet aggregate in the DB in a transaction.
        """
        try:
            with self.database:
                self._upsert_folderset(folderset)
                root_folder_list = [str(folder) for folder in folderset.folders.keys()]
                inserted_directory_id_list = self._insert_root_directories(root_folder_list)
                self._insert_reflective_closure_nodes(inserted_directory_id_list)
                folderset_data =[(str(f.path), f.enabled, folderset.id) for f in folderset.all]
                self._insert_root_folders(folderset_data)
                self._prune_root_folders(root_folder_list, folderset.id)
                self._prune_directories_without_root()
        except sqlite3.DatabaseError as e:
            raise PersistenceError("Failed to save folderset") from e

    def add_folderset(self, folderset_name: str) -> int:
        """
        Adds a folderset to the DB.
        Returns the unique id of the added folderset.
        """
        try:
            with self.database:
                cursor = self.database.execute(
                    """
                    INSERT INTO foldersets (name) VALUES (?) RETURNING id;
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
                self._prune_directories_without_root()
        except sqlite3.DatabaseError as e:
            raise PersistenceError("Failed to delete folderset") from e

    # Private Helpers:

    def _insert_root_directories(self, root_folders: list[str]) ->list[int]:
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

    def _prune_directories_without_root(self) -> None:
        self.database.execute(
            """
            DELETE FROM directories WHERE dir_id NOT IN (
            SELECT descendant_id FROM folders_closure WHERE ancestor_id IN (
            SELECT id FROM rootfolders))
            """
        )

    def _insert_reflective_closure_nodes(self, dir_id_list: list[int]) -> None:
        if dir_id_list:
            directory_data = [(directory_id, directory_id) for directory_id in dir_id_list]
            self.database.executemany(
                """
                INSERT INTO folders_closure (ancestor_id, descendant_id, depth)
                VALUES (?, ?, 0)
                """,
                directory_data)

    def _upsert_folderset(self, folderset: FolderSet) -> None:
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


class SQLDirectoryRepository(DirectoryRepository):

    def __init__(
        self,
        database: SQLite3Database,
    ) -> None:
        self.database = database

    def add_discovered_folder(self, dir_name: str, parent_id, crawl_time: int, mod_time: int) -> int:
        new_dir_id = self._add_directory_node(dir_name, crawl_time, mod_time)
        self._add_closure_edges(parent_id, new_dir_id)
        return new_dir_id

    def get_all_directories(self) ->tuple[dict[int,str], dict[int,dict[str, str|int|set[int]]]]:
        query = """ 
        SELECT c.descendant_id,d.dir_id, d.dir_name, d.crawl_time, d.mod_time from directories d
        INNER JOIN folders_closure c ON d.dir_id = c.ancestor_id WHERE c.depth = 1 OR 
            (c.depth = 0 AND dir_id IN (SELECT dir_id FROM rootfolders))
        """
        root_map = {}
        edges = {}
        for directory in self.database.execute(query).fetchall():
            edges.setdefault(directory["dir_id"],{
                "dir_name": directory["dir_name"],
                "crawl_time": directory["crawl_time"],
                "mod_time": directory["mod_time"],
                "children": set(),
            })
            if directory["dir_id"] != directory["descendant_id"]:
                edges[directory["dir_id"]]["children"].add(directory["descendant_id"])
            else:
                root_map[directory["dir_id"]] = directory["dir_name"]
        return root_map, edges

    def get_normalized_path(self, dir_id: int) -> Path:
        query = """ 
        SELECT dir_name 
        FROM directories d 
        INNER JOIN folders_closure c ON d.dir_id = c.ancestor_id 
        WHERE c.descendant_id = ? 
        ORDER BY c.depth DESC
        """
        cursor = self.database.execute(query, (dir_id,)).fetchall()
        return Path(*[segment["dir_name"] for segment in cursor])

    def update_dir(self, dir_id: int, crawl_time: int, mod_time: int) -> None:
        query = """
        UPDATE directories SET crawl_time = ?, mod_time = ? WHERE dir_id = ?
        """
        self.database.execute(query, (crawl_time, mod_time, dir_id))

    def _add_directory_node(self, dir_name: str, crawl_time: int, mod_time: int) -> int:
        query = """
                INSERT INTO directories (dir_name, crawl_time, mod_time) 
                VALUES (?, ?, ?) RETURNING dir_id; 
                """
        return self.database.execute(query, (dir_name, crawl_time, mod_time)).fetchone()["dir_id"]

    def _add_closure_edges(self, parent_id: int, current_dir_id: int) -> None:
        self.database.execute("""
                              INSERT INTO folders_closure (ancestor_id, descendant_id, depth)
                              SELECT c.ancestor_id, ?, c.depth + 1
                              FROM folders_closure c
                              WHERE descendant_id = ?
                              """, [current_dir_id, parent_id])
        self.database.execute(
            "INSERT INTO folders_closure (ancestor_id, descendant_id, depth) VALUES (?, ?, 0)",
            (current_dir_id, current_dir_id),
        )