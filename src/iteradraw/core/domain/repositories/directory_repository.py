import logging
import sqlite3
from pathlib import Path

from iteradraw.core.domain.exceptions import PersistenceError
from iteradraw.core.infrastructure.persistence.sqlite3_database import \
    SQLite3Database
from iteradraw.interfaces import DirectoryRepository

logger = logging.getLogger(__name__)

class SQLite3DirectoryRepository(DirectoryRepository):
    """
    Repository class managing internal directory tree.

    Tables:
        - directories: Directory metadata and identity.
        - folders_closure: Directory relations to other directories.
    """

    def __init__(self, database: SQLite3Database) -> None:
        self.database = database

    def create_directory(self, dir_name: str, parent_id: int,
                         crawl_time: int = 0, mod_time: int = 0) -> int:
        """
        Adds directory node and closure edges to database.

        Needs to have deduplication added once all directories are hierarchical.
        Args:
            dir_name: Name of directory to be created.
            parent_id:  ID of containing parent directory in database.
            crawl_time: Timestamp of last crawl.
            mod_time: Timestamp of last modification.
        """
        dir_id = self._register_node(dir_name, crawl_time, mod_time)
        self._register_node_edges(parent_id, dir_id)
        return dir_id

    def create_directories(self, dirs: list[Path]) -> list[int]:
        """ todo rename this method meant for roots
        Bulk adds directory nodes and closure edges to database.

        This method relies on materializing the full path
        to directory dupe candidates in order to perform deduplication.
        Expensive if user has many directories with the same name.
        """
        new_dirs = []
        for dir_name in dirs:
            if not self.is_duplicate(dir_name):
                new_dirs.append(str(dir_name))
        dir_ids = self._register_node_batch(new_dirs)
        self._register_node_reflection_batch(dir_ids)
        return list(zip(dir_ids, new_dirs))

    def update_directory(self, dir_id: int, crawl_time: int = 0,
                         mod_time: int = 0) -> None:
        """
        Updates metadata for a directory.

        Args:
            dir_id: ID of directory in database.
            crawl_time: Timestamp of last crawl.
            mod_time: Timestamp of last modification.
        Raises:
            PersistenceError: Error while updating directory.
        """
        try:
            query = """
                UPDATE directories 
                SET crawl_time = ?, mod_time   = ? 
                WHERE dir_id = ? 
            """
            self.database.execute(query, (crawl_time, mod_time, dir_id))
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error while updating directory") from e

    def get_directories(self) -> dict[int, dict[str, str | int | set | bool]]:
        """
        Returns all directories and their metadata and materialized path keyed
        by ID.

        This method crosses boundary into folderset/rootfolders managed by
        FolderRepository. Problem with this is that rootfolder modifications
        before calling this method may cause inconsistent behavior.
        """
        graph = self._build_directory_graph()
        finished = {}
        for item in graph.items():
            if not item[1]["is_root"]:
                continue
            root_id, root_data = item
            root_data["path"] = root_data["dir_name"]
            finished[root_id] = root_data
            materialize = [(graph[root_id], root_data["dir_name"])]
            while materialize:
                dir_data, path_to_ancestor = materialize.pop()
                for child in dir_data["children"]:
                    path_to_child = str(Path(path_to_ancestor).joinpath(
                        graph[child]["dir_name"])
                    )
                    materialize.append((graph[child], path_to_child))
                    graph[child]["path"] = path_to_child
                    finished[child] = graph[child]
        return finished

    def is_duplicate(self, dir_path: Path) -> int | None:
        """
        Returns ID if there is a match in the database else returns None.

        Naive approach to deduplication, less expensive than the greedy
        check against all directories in the database but still can be improved.
        Meant for full absolute paths.
        """
        dir_name = dir_path.name
        query = """
            SELECT dir_id
            FROM directories d
            WHERE d.dir_name = ?
        """
        candidate_ids = [
            directory["dir_id"] for directory in self.database.execute(
                query, (dir_name,)).fetchall()
        ]
        for candidate_id in candidate_ids:
            if self.get_normalized_path(candidate_id) == dir_path:
                return candidate_id
        return None

    def get_normalized_path(self, dir_id: int) -> Path:
        """
        Returns materialized path for given directory.
        """
        query = """
            SELECT dir_name 
            FROM directories d
            INNER JOIN folders_closure c 
            ON d.dir_id = c.ancestor_id
            WHERE c.descendant_id = ? 
            ORDER BY c.depth DESC 
        """
        cursor = self.database.execute(query, (dir_id,)).fetchall()
        return Path(*[segment["dir_name"] for segment in cursor])

    def _build_directory_graph(self) -> dict[int, dict[str, str | int | set | bool]]:
        """
        Returns dict of all directories and their metadata and folder hierarchy.

        This method crosses boundary into folderset/rootfolders managed by
        FolderRepository. Problem with this is that rootfolder modifications
        before calling this method may cause inconsistent behavior.
        """
        query = """
            SELECT c.descendant_id, d.dir_id, d.dir_name, d.crawl_time, d.mod_time 
            from directories d INNER JOIN folders_closure c  
            ON d.dir_id = c.ancestor_id WHERE c.depth = 1 
            OR (c.depth = 0 AND dir_id IN (SELECT dir_id FROM rootfolders)) 
        """
        edges = {}
        for directory in self.database.execute(query).fetchall():
            edges.setdefault(directory["dir_id"], {
                "dir_name": directory["dir_name"],
                "crawl_time": directory["crawl_time"],
                "mod_time": directory["mod_time"],
                "children": set(),
                "is_root": False,
            })
            if directory["dir_id"] != directory["descendant_id"]:
                edges[directory["dir_id"]]["children"].add(directory["descendant_id"])
            else:
                edges[directory["dir_id"]]["is_root"] = True
        return edges

    def _register_node(self, dir_name: str, crawl_time: int = 0,
                       mod_time: int = 0) -> int:
        """
        Registers directory node.

        Does not register closure edges between nodes.

        Raises:
            PersistenceError: Error registering directory
        """
        try:
            query = """
                INSERT INTO directories (dir_name, crawl_time, mod_time)
                VALUES (?, ?, ?) RETURNING dir_id; 
            """
            return self.database.execute(query, (dir_name, crawl_time, mod_time)).fetchone()["dir_id"]
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error registering directory") from e

    def _register_node_batch(self, dirs: list[str]) -> list[int]:
        """
        Bulk registers directory nodes.

        Raises:
            PersistenceError: Error bulk registering directories.
        """
        try:
            if not dirs:
                return []
            insert_folders_query = " ".join(
                ["INSERT INTO directories (dir_name, crawl_time, mod_time) VALUES",
                 ", ".join(["(?, 0, 0)" for _ in range(len(dirs))]), ]
            )
            rows = self.database.execute(insert_folders_query, dirs).fetchall()
            return [(directory_id["dir_id"]) for directory_id in rows]
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error bulk registering directories") from e

    def _register_node_edges(self, parent_id: int, child_id: int) -> None:
        """
        Registers edge between child and every ancestor.

        Raises:
            PersistenceError: Error registering edges.
        """
        try:
            query = """
                INSERT INTO folders_closure (ancestor_id, descendant_id, depth)
                SELECT c.ancestor_id, ?, c.depth + 1
                FROM folders_closure c
                WHERE descendant_id = ?
            """
            self.database.execute(query, [child_id, parent_id])
            self._register_node_reflection_batch([child_id])
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error registering edges") from e

    def _register_node_reflection_batch(self, dir_ids: list) -> None:
        """
        Bulk registers reflective closure edges for many directory nodes.

        This bulk insert inserts only reflective (self-referential) edges.
        For ancestor/descendant registration use _register_node_edges.

        Raises:
            PersistenceError: Error registering node reflection.
        """
        try:
            query = "INSERT INTO folders_closure (ancestor_id, descendant_id, depth) VALUES (?, ?, 0)"
            self_refs = [(dir_id, dir_id) for dir_id in dir_ids]
            self.database.executemany(query, self_refs)
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError("Error registering node reflection") from e

    def _prune_directories_without_root(self) -> None:
        """
        Prunes directories without root folder registered.

        This method crosses boundary into folderset/rootfolders managed by
        FolderRepository. Problem with this is that rootfolder modifications
        may cause inconsistent behavior.

        Raises:
            PersistenceError: Error pruning directories without roots.
        """
        try:
            query = """
                DELETE
                FROM directories
                WHERE dir_id NOT IN 
                (SELECT descendant_id
                 FROM folders_closure
                 WHERE ancestor_id IN 
                  (SELECT id
                   FROM rootfolders))
            """
            self.database.execute(query)
        except sqlite3.DatabaseError as e:
            logger.error(e)
            raise PersistenceError(
                "Error pruning directories without roots"
            ) from e