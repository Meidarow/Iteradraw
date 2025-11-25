import uuid
from uuid import UUID

from iteradraw.interfaces import IdGenerator


class UUIDGenerator(IdGenerator):
    def generate(self) -> UUID:
        return uuid.uuid4()
