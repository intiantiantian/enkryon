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

def insert_account(name):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('INSERT INTO accounts (name) VALUES (?)', (name,))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        connection.close()

def delete_account(account_id):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
    connection.commit()
    connection.close()

def get_all_accounts():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM accounts')
    accounts = cursor.fetchall()
    connection.close()
    return accounts