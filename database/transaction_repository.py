import sqlite3
from .connection import connect_database

def create_transactions_table():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category_id INTEGER NOT NULL,
            date_time TEXT NOT NULL,
            notes TEXT,
                   
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    connection.commit()
    connection.close()

def insert_transaction(account, amount, category, date_time, notes):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO transactions (account_id, amount, category_id, date_time, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (account, amount, category, date_time, notes))
    connection.commit()
    connection.close()

def get_all_transactions():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''SELECT transactions.id, accounts.name, category_groups.name,
                   categories.name, transactions.amount, transactions.date_time,
                   transactions.notes, category_groups.transaction_type
                   FROM transactions
                   INNER JOIN accounts ON transactions.account_id = accounts.id
                   INNER JOIN categories ON transactions.category_id = categories.category_id
                   INNER JOIN category_groups ON categories.group_id = category_groups.group_id
                   ORDER BY transactions.date_time DESC
                   ''')
    transactions = cursor.fetchall()
    connection.close()
    return transactions

def get_transaction_by_id(transaction_id):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''SELECT transactions.id, transactions.account_id, transactions.amount,
                   transactions.category_id, transactions.date_time, transactions.notes,
                   accounts.name, categories.name, categories.group_id, category_groups.name,
                   category_groups.transaction_type
                   FROM transactions
                   INNER JOIN accounts ON transactions.account_id = accounts.id
                   INNER JOIN categories ON transactions.category_id = categories.category_id
                   INNER JOIN category_groups ON categories.group_id = category_groups.group_id
                   WHERE transactions.id = ?
                   ''', (transaction_id,))
    transaction = cursor.fetchone()
    connection.close()
    return transaction


def update_transaction(account, amount, category, date_time, notes, transaction_id):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''UPDATE transactions 
                        SET account_id = ?, amount = ?,
                       category_id = ?, date_time = ?, notes = ?
                        WHERE id = ?''', (account, amount, category, date_time, notes, transaction_id))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def delete_transaction(transaction_id):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.commit()
        connection.close()