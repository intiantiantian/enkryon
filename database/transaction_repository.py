import sqlite3
from .connection import connect_database

def create_transactions_table(connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = connect_database()

    try:
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
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        ''')

        if owns_connection:
            connection.commit()
    finally:
        if owns_connection:
            connection.close()

def insert_transaction(
    account_id,
    amount_centavos,
    category_id,
    date_time,
    notes,
):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO transactions (
            account_id,
            amount_centavos,
            category_id,
            date_time,
            notes
        )
        VALUES (?, ?, ?, ?, ?)
    ''', (
        account_id,
        amount_centavos,
        category_id,
        date_time,
        notes,
    ))
    connection.commit()
    connection.close()

def get_transactions(limit=None, account_id=None, transaction_type=None):
    connection = connect_database()
    cursor = connection.cursor()
    query = '''SELECT transactions.id,
                accounts.name,
                category_groups.name,
                categories.name,
                transactions.amount_centavos,
                transactions.date_time,
                transactions.notes,
                category_groups.transaction_type
                FROM transactions
                INNER JOIN accounts ON transactions.account_id = accounts.id
                INNER JOIN categories ON transactions.category_id = categories.category_id
                INNER JOIN category_groups ON categories.group_id = category_groups.group_id
            '''
    
    conditions = []
    params = []

    if account_id is not None:
        conditions.append('transactions.account_id = ?')
        params.append(account_id)

    if transaction_type is not None:
        conditions.append('category_groups.transaction_type = ?')
        params.append(transaction_type)

    if conditions:
        query += ' WHERE ' + " AND ".join(conditions)

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
                   transactions.amount_centavos,
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

def update_transaction(
    account_id,
    amount_centavos,
    category_id,
    date_time,
    notes,
    transaction_id,
):
    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            '''
            UPDATE transactions
            SET account_id = ?,
                amount_centavos = ?,
                category_id = ?,
                date_time = ?,
                notes = ?
            WHERE id = ?
            ''',
            (
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes,
                transaction_id,
            ),
        )
        connection.commit()
        return True
    except sqlite3.Error as error:
        print(error)
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

def get_total_centavos(transaction_type, account_id=None):
    connection = connect_database()
    cursor = connection.cursor()

    try:
        query = '''
            SELECT SUM(amount_centavos)
            FROM transactions
            INNER JOIN categories
                ON transactions.category_id = categories.category_id
            INNER JOIN category_groups
                ON categories.group_id = category_groups.group_id
            WHERE transaction_type = ?
        '''

        params = [transaction_type]

        if account_id is not None:
            query += " AND transactions.account_id = ?"
            params.append(account_id)

        cursor.execute(query, tuple(params))
        amount_centavos = cursor.fetchone()[0]

        return int(amount_centavos or 0)
    except sqlite3.Error as error:
        print(error)
        return False
    finally:
        connection.close()


def get_current_balance_centavos(account_id=None):
    return (
        get_total_centavos("income", account_id)
        - get_total_centavos("expense", account_id)
    )