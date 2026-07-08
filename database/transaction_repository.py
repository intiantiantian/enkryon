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

def get_transactions(limit=None, account_id=None):
    connection = connect_database()
    cursor = connection.cursor()
    query = '''SELECT transactions.id,
                accounts.name,
                category_groups.name,
                categories.name,
                transactions.amount,
                transactions.date_time,
                transactions.notes,
                category_groups.transaction_type
                FROM transactions
                INNER JOIN accounts ON transactions.account_id = accounts.id
                INNER JOIN categories ON transactions.category_id = categories.category_id
                INNER JOIN category_groups ON categories.group_id = category_groups.group_id
            '''
    
    params = []

    if account_id is not None:
        query += 'WHERE transactions.account_id = ?'
        params.append(account_id)

    query += ' ORDER BY transactions.date_time DESC, transactions.id DESC'
    
    if limit is not None:
        query += ' LIMIT ?'
        params.append(limit)

    cursor.execute(query, tuple(params))
    transactions = cursor.fetchall()
    connection.close()
    return transactions

def get_transaction_by_id(transaction_id):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''SELECT transactions.id,
                   transactions.account_id,
                   transactions.amount,
                   transactions.category_id,
                   transactions.date_time,
                   transactions.notes,
                   accounts.name,
                   categories.name,
                   categories.group_id,
                   category_groups.name,
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
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def get_total_income(account_id=None):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        query = '''SELECT SUM(amount)
                       FROM transactions
                       INNER JOIN categories ON transactions.category_id = categories.category_id
                       INNER JOIN category_groups ON categories.group_id = category_groups.group_id
                       WHERE transaction_type = 'income'
                '''
        
        params = []

        if account_id is not None:
            query += ' AND transactions.account_id = ?'
            params.append(account_id)

        cursor.execute(query, tuple(params))
        amount = cursor.fetchone()[0]
        return float(amount or 0)
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def get_total_expense(account_id=None):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        query = '''SELECT SUM(amount)
                       FROM transactions
                       INNER JOIN categories ON transactions.category_id = categories.category_id
                       INNER JOIN category_groups ON categories.group_id = category_groups.group_id
                       WHERE transaction_type = 'expense'
                '''
        
        params = []

        if account_id is not None:
            query += ' AND transactions.account_id = ?'
            params.append(account_id)

        cursor.execute(query, tuple(params))
        amount = cursor.fetchone()[0]
        return float(amount or 0)
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def get_current_balance(account_id=None):
    return get_total_income(account_id) - get_total_expense(account_id)