from contextlib import contextmanager

import sqlite3

from database.path import get_database_path


def connect_database():
    connection = sqlite3.connect(get_database_path())
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def managed_connection():
    connection = connect_database()

    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
