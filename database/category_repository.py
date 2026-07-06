from .connection import connect_database

def create_categories_table():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
            type TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

def insert_category(name, type):    
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO categories (name, type)
        VALUES (?, ?)
    ''', (name, type))
    connection.commit()
    connection.close()

def get_categories_by_type(type):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM categories WHERE type = ?', (type,))
    categories = cursor.fetchall()
    connection.close()
    return categories