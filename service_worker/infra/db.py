"""Database wrapper helpers specific to the worker service."""

from taskflow_core import Database


database: Database | None = None


def create_database(url: str, *, echo: bool = False) -> Database:
    """Instantiate and cache an async Database helper for the worker."""
    global database
    database = Database(url, echo=echo)
    return database
