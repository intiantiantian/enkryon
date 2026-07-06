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