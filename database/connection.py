import sqlite3

DATABASE_NAME = 'database/database.db'


def connect_database():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection