from taskflow_core import Database


database: Database | None = None


def create_database(url: str, *, echo: bool = False) -> Database:
    global database
    database = Database(url, echo=echo)
    return database
