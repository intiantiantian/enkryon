import sqlite3

from database.path import get_database_path


def connect_database():
    connection = sqlite3.connect(get_database_path())
    connection.execute("PRAGMA foreign_keys = ON")
    return connection