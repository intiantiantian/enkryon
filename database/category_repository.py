import sqlite3

from .connection import connect_database

def create_categories_table():
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                UNIQUE(group_id, name),
                FOREIGN KEY (group_id) REFERENCES category_groups(group_id)
            )
        ''')
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def insert_category(group_id, name):    
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO categories (group_id, name)
            VALUES (?, ?)
        ''', (group_id, name))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def update_category(category_id, name):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            UPDATE categories
            SET name = ?
            WHERE category_id = ?
        ''', (name, category_id))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def delete_category(category_id):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('DELETE FROM categories WHERE category_id = ?', (category_id,))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def get_all_categories():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT categories.category_id, categories.group_id, categories.name,
               category_groups.name, category_groups.transaction_type
        FROM categories
        INNER JOIN category_groups ON categories.group_id = category_groups.group_id
        ORDER BY category_groups.name, categories.name
    ''')
    categories = cursor.fetchall()
    connection.close()
    return categories

def get_categories_by_group(group_id):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT categories.category_id, categories.group_id, categories.name,
               category_groups.name, category_groups.transaction_type
        FROM categories
        INNER JOIN category_groups ON categories.group_id = category_groups.group_id
        WHERE categories.group_id = ?
        ORDER BY categories.name COLLATE NOCASE
    ''', (group_id,))
    categories_by_group = cursor.fetchall()
    connection.close()
    return categories_by_group

def get_categories_by_type(transaction_type):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT categories.category_id, categories.group_id, categories.name,
               category_groups.name, category_groups.transaction_type
        FROM categories
        INNER JOIN category_groups ON categories.group_id = category_groups.group_id
        WHERE category_groups.transaction_type = ?
        ORDER BY category_groups.name, categories.name
    ''', (transaction_type,))
    categories_by_type = cursor.fetchall()
    connection.close()
    return categories_by_type