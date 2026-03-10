from typing import Iterable, Any

from iteradraw.interfaces import ImageRepository


class SQLImageRepository(ImageRepository):

    def __init__(
        self, database
    ):
        self.database = database

    def insert_image_batch(self, batch: Iterable[Any]) -> None:
        query = """
        INSERT INTO images (name, parent_id) VALUES (?, ?)
        """
        self.database.executemany(query, batch)

    def clear_images_under_parent(self, parent_id: int) -> None:
        query = """
        DELETE FROM images WHERE parent_id = ?
        """
        self.database.execute(query, (parent_id,))