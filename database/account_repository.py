import sqlite3

from .connection import connect_database

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
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM accounts ORDER BY name COLLATE NOCASE')
    accounts = cursor.fetchall()
    connection.close()
    return accounts


def get_account_by_id(account_id):
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (account_id,)
    )

    account = cursor.fetchone()
    connection.close()

    return account


def insert_account(name):
    connection = connect_database()
    cursor = connection.cursor()
    name = (name or "").strip()

    if not name:
        connection.close()
        return False

    try:
        if account_name_exists(cursor, name):
            return False

        cursor.execute(
            "INSERT INTO accounts (name) VALUES (?)",
            (name,),
        )
        connection.commit()
        return True
    except sqlite3.Error as error:
        print(error)
        return False
    finally:
        connection.close()


def update_account(account_id, name):
    connection = connect_database()
    cursor = connection.cursor()
    name = (name or "").strip()

    if not name:
        connection.close()
        return False

    try:
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
    except sqlite3.Error as error:
        print(error)
        return False
    finally:
        connection.close()


def delete_account(account_id):
    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM transactions WHERE account_id = ?",
            (account_id,)
        )

        transaction_count = cursor.fetchone()[0]

        if transaction_count > 0:
            return False, "referenced"

        cursor.execute(
            "DELETE FROM accounts WHERE id = ?",
            (account_id,)
        )

        connection.commit()
        return True, None

    except sqlite3.Error as e:
        print(e)
        return False, "error"

    finally:
        connection.close()