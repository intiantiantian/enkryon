import sqlite3

from .connection import connect_database

def create_accounts_table():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')     
    connection.commit()
    connection.close()

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
    try:
        cursor.execute('INSERT INTO accounts (name) VALUES (?)', (name,))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def update_account(account_id, name):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('UPDATE accounts SET name = ? WHERE id = ?', (name, account_id))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
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