import sqlite3

from .connection import managed_connection


def clear_database():
    try:
        with managed_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("DELETE FROM account_transfers")
            cursor.execute("DELETE FROM transactions")
            cursor.execute("DELETE FROM categories")
            cursor.execute("DELETE FROM category_groups")
            cursor.execute("DELETE FROM accounts")

            connection.commit()
            return True
    except sqlite3.Error:
        return False
