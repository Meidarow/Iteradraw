class DatabaseError(Exception):
    pass

class PersistenceError(DatabaseError):
    """Error raised when a transaction fails"""

class CommitError(DatabaseError):
    """Error when attempting to commit rows to chosen database."""

class DatabaseConnectionError(DatabaseError):
    """No connection to database"""
