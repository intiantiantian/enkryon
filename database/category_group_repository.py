import sqlite3

from .connection import connect_database

def create_category_groups_table():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category_groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            UNIQUE(name, transaction_type)
        )
    ''')
    connection.commit()
    connection.close()

def insert_category_group(name, transaction_type):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO category_groups (name, transaction_type)
            VALUES (?, ?)
        ''', (name, transaction_type))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def update_category_group(group_id, name):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            UPDATE category_groups
            SET name = ?
            WHERE group_id = ?
        ''', (name, group_id))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def delete_category_group(group_id):
    connection = connect_database()
    cursor = connection.cursor()
    try:
        cursor.execute('DELETE FROM category_groups WHERE group_id = ?', (group_id,))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False
    finally:
        connection.close()

def get_all_category_groups():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM category_groups ORDER BY name')
    category_groups = cursor.fetchall()
    connection.close()
    return category_groups

def get_category_groups_by_type(transaction_type):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM category_groups WHERE transaction_type = ? ORDER BY name COLLATE NOCASE', (transaction_type,))
    category_groups = cursor.fetchall()
    connection.close()
    return category_groups