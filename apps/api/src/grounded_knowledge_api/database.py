from collections.abc import Callable

import psycopg


def check_connection(database_url: str) -> bool:
    """Return whether PostgreSQL accepts a short-lived health-check connection."""
    with psycopg.connect(database_url, connect_timeout=2) as connection:
        connection.execute("SELECT 1")
    return True


def database_checker(database_url: str) -> Callable[[], bool]:
    """Create an injectable database health checker for the API boundary."""
    return lambda: check_connection(database_url)
