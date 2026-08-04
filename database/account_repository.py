import sqlite3

from .connection import connect_database, managed_connection
from .records import AccountRecord

def create_accounts_table(connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = connect_database()

    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        if owns_connection:
            connection.commit()
    finally:
        if owns_connection:
            connection.close()


def account_name_exists(
    cursor,
    name,
    exclude_account_id=None,
):
    query = '''
        SELECT 1
        FROM accounts
        WHERE lower(trim(name)) = lower(trim(?))
    '''
    params = [name]

    if exclude_account_id is not None:
        query += " AND id != ?"
        params.append(exclude_account_id)

    cursor.execute(query, tuple(params))
    return cursor.fetchone() is not None


def get_all_accounts():
    with managed_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            'SELECT * FROM accounts ORDER BY name COLLATE NOCASE'
        )
        return [AccountRecord(*row) for row in cursor.fetchall()]


def get_account_by_id(account_id):
    with managed_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,)
        )
        row = cursor.fetchone()

    if row is None:
        return None

    return AccountRecord(*row)


def insert_account(name):
    name = (name or "").strip()

    if not name:
        return False

    try:
        with managed_connection() as connection:
            cursor = connection.cursor()

            if account_name_exists(cursor, name):
                return False

            cursor.execute(
                "INSERT INTO accounts (name) VALUES (?)",
                (name,),
            )
            connection.commit()
            return True
    except sqlite3.Error:
        return False


def update_account(account_id, name):
    name = (name or "").strip()

    if not name:
        return False

    try:
        with managed_connection() as connection:
            cursor = connection.cursor()

            if account_name_exists(
                cursor,
                name,
                exclude_account_id=account_id,
            ):
                return False

            cursor.execute(
                "UPDATE accounts SET name = ? WHERE id = ?",
                (name, account_id),
            )

            if cursor.rowcount == 0:
                return False

            connection.commit()
            return True
    except sqlite3.Error:
        return False


def delete_account(account_id):
    try:
        with managed_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                '''
                SELECT
                    EXISTS(
                        SELECT 1
                        FROM transactions
                        WHERE account_id = ?
                    )
                    OR EXISTS(
                        SELECT 1
                        FROM account_transfers
                        WHERE source_account_id = ?
                           OR destination_account_id = ?
                    )
                ''',
                (account_id, account_id, account_id),
            )

            is_referenced = bool(cursor.fetchone()[0])

            if is_referenced:
                return False, "referenced"

            cursor.execute(
                "DELETE FROM accounts WHERE id = ?",
                (account_id,)
            )

            connection.commit()
            return True, None
    except sqlite3.Error:
        return False, "error"
