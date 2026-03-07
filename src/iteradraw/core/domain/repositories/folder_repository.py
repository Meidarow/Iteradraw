from uuid import UUID

from iteradraw.core.domain.models.folder import FolderSet
from iteradraw.core.infrastructure.persistence.sqlite3_database import (
    SQLite3DomainDatabase,
)
from iteradraw.interfaces import FolderRepository


class SQLFolderRepository(FolderRepository):
    """
    Repository for FolderSet domain objects.

    Facilitates persistence operations for the FolderSet model by
    abstracting backend implementations and providing (de-)serialization
    methods. Allows for backend injection, as long as implementation follows
    the Persistence protocol.

    Handles only FolderSets since an individual Folder is not meant to exist
    outside a folder set.
    """

    def __init__(self, persistence: SQLite3DomainDatabase):
        self.persistence = persistence

    def get(self, folderset_id: UUID) -> FolderSet:
        folderset_id_str = str(folderset_id)
        return self.persistence.get_folderset(folderset_id=folderset_id_str)

    def get_all(self) -> list[FolderSet]:
        return self.persistence.get_all_foldersets()

    def save(self, folderset: FolderSet):
        self.persistence.save_folderset(folderset=folderset)

    def remove(self, folderset_id: UUID):
        folderset_id_str = str(folderset_id)
        self.persistence.delete_folderset(folderset_id=folderset_id_str)

    DB_SCHEMA = """
    CREATE TABLE IF NOT EXISTS foldersets (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS rootfolders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        enabled BOOLEAN DEFAULT 1,
        folderset_id INT NOT NULL,
        FOREIGN KEY(folderset_id) REFERENCES foldersets(id)
        ON DELETE CASCADE,
        FOREIGN KEY (id) REFERENCES discovered_folders(dir_id)
    );
        
    CREATE TABLE IF NOT EXISTS discovered_folders (
        dir_id INTEGER NOT NULL PRIMARY KEY,
        dir_name TEXT NOT NULL,
        crawl_time INT NOT NULL,
        mod_time INT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS folders_closure (
        ancestor_id INT NOT NULL,
        descendant_id INT NOT NULL,
        depth INT NOT NULL,
        PRIMARY KEY (ancestor_id, descendant_id),
        FOREIGN KEY (ancestor_id) REFERENCES discovered_folders(dir_id),
        FOREIGN KEY (descendant_id) REFERENCES discovered_folders(dir_id)
    );
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.database:
            try:
                self.database.close()
            finally:
                self.database = None

    def __init__(
        self,
        db_path: Optional[str] = None,
        connection: Optional[sqlite3.Connection] = None,
    ) -> None:
        self.db_path = db_path
        if db_path is None and connection is None:
            raise ValueError(
                "Must provide either db_path or an open sqlite3.Connection"
            )
        self.database = connection or sqlite3.connect(self.db_path)
        self.database.row_factory = sqlite3.Row
        self.setup_schema()
        self._configure_connection()

    def initialize(self) -> None:
        """Open the connection and ensure the schema exists."""
        self.setup_schema()  # create table if it isn’t there

    def clear_all(self) -> None:
        """Drop all folder tables."""
        query = """
        DROP TABLE IF EXISTS folders;
        DROP TABLE IF EXISTS foldersets;
        """
        with self.database:
            self.database.executescript(query)

    def setup_schema(self, db_schema: str | None = None) -> None:
        """Create table with db_schema."""
        query = db_schema or self.DB_SCHEMA
        with self.database:
            self.database.executescript(query)

    def get_folderset(self, folderset_id: str) -> FolderSet:
        """
        Retrieves one FolderSet from the DB and reconstructs the aggregate.
        """
        fs_row = self._execute(
            "SELECT name FROM foldersets WHERE id = ?", (folderset_id,)
        ).fetchone()

        if not fs_row:
            raise ObjectNotFoundError(
                f"No FolderSet found with UUID: {folderset_id}"
            )
        folder_rows = self._execute(
            "SELECT path, enabled FROM folders WHERE folderset_id = ?",
            (folderset_id,),
        ).fetchall()

        # noinspection PyArgumentList
        return FolderSet(
            uuid=uuid.UUID(folderset_id),
            display_name=fs_row["name"],
            folders={
                row["path"]: Folder(row["path"], row["enabled"])
                for row in folder_rows
            },
        )

    def get_all_foldersets(self) -> list[FolderSet]:
        """
        Retrieves all FolderSets from the DB and reconstructs them.
        """

        # 1. Get ALL data in one go
        query = """
        SELECT
            fs.id,
            fs.name,
            f.path,
            f.enabled
        FROM
            foldersets fs
        LEFT JOIN
            folders f ON f.folderset_id = fs.id
        ORDER BY
            fs.id;
        """

        # This holds the in-progress foldersets: { "name": { "path": folder } }
        foldersets_map = {}

        # 2. Loop through the flat results
        # (Assuming your _execute.fetchall() returns dict-like rows)
        for row in self._execute(query).fetchall():
            folderset_id = row["id"]
            folderset_name = row["name"]

            # 3. Create the FolderSet if it's the first time we've seen it
            if folderset_id not in foldersets_map:
                foldersets_map[folderset_id] = {
                    "name": folderset_name,
                    "folders": {},
                }

            # 4. Add the folder to its set
            if row["path"]:
                foldersets_map[folderset_id]["folders"][row["path"]] = Folder(
                    path=row["path"], enabled=row["enabled"]
                )

        # noinspection PyArgumentList
        return [
            FolderSet(
                uuid=uuid.UUID(folderset_id),
                display_name=data["name"],
                folders=data["folders"],
            )
            for folderset_id, data in foldersets_map.items()
        ]

    def save_folderset(self, folderset: FolderSet):
        """
        Saves a FolderSet aggregate to the DB in a transaction.
        """
        try:
            with self.database:
                cursor = self._execute(
                    """
                    INSERT INTO foldersets (id, name) VALUES (?, ?)
                    ON CONFLICT(id) DO UPDATE SET name=excluded.name
                    RETURNING id
                    """,
                    (folderset.uuid, folderset.display_name),
                )
                folderset_id = cursor.fetchone()["id"]

                # Nuke old folders for this set (simple, effective)
                self._execute(
                    "DELETE FROM folders WHERE folderset_id = ?",
                    (folderset_id,),
                )

                # Insert new folders
                folder_data = [
                    (f.path, f.enabled, folderset_id) for f in folderset.all
                ]
                if folder_data:  # executemany fails on empty list
                    self.database.executemany(
                        """
                        INSERT INTO folders (path, enabled, folderset_id)
                        VALUES (?, ?, ?)
                        """,
                        folder_data,
                    )
        except sqlite3.DatabaseError as e:
            raise PersistenceError("Failed to save folderset") from e

    def delete_folderset(self, folderset_id):
        try:
            with self.database:
                self._execute(
                    "DELETE FROM foldersets WHERE id = ?",
                    (folderset_id,),
                )
        except sqlite3.DatabaseError as e:
            raise PersistenceError("Failed to delete folderset") from e

    def commit(self) -> None:
        """Explicitly commit any pending transaction."""
        try:
            if self.database:
                self.database.commit()
                self.database.execute("PRAGMA wal_checkpoint(FULL);")
        except sqlite3.DatabaseError as e:
            raise CommitError("Failed to commit to database") from e

    def _configure_connection(self):
        self.database.execute("PRAGMA journal_mode = WAL;")
        self.database.execute("PRAGMA synchronous = NORMAL;")
        self.database.execute("PRAGMA temp_store = MEMORY;")
        self.database.execute("PRAGMA foreign_keys = ON;")

    def _execute(self, query: str, params: Any = ()) -> sqlite3.Cursor:
        """Run a single statement with optional parameters."""
        return self.database.execute(query, params)
