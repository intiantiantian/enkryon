import sqlite3

from .connection import connect_database
from .records import CategoryRecord

def create_categories_table(connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = connect_database()

    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                UNIQUE(group_id, name),
                FOREIGN KEY (group_id) REFERENCES category_groups(group_id)
            )
        ''')

        if owns_connection:
            connection.commit()

        return True
    except sqlite3.Error as error:
        if not owns_connection:
            raise

        print(error)
        return False
    finally:
        if owns_connection:
            connection.close()

def category_name_exists_for_type(cursor, name, transaction_type, exclude_category_id=None):
    query = '''
        SELECT 1
        FROM categories
        INNER JOIN category_groups
            ON categories.group_id = category_groups.group_id
        WHERE LOWER(TRIM(categories.name)) = LOWER(TRIM(?))
        AND category_groups.transaction_type = ?
    '''

    params = [name, transaction_type]

    if exclude_category_id is not None:
        query += ' AND categories.category_id != ?'
        params.append(exclude_category_id)

    cursor.execute(query, tuple(params))
    return cursor.fetchone() is not None

def insert_category(group_id, name):
    connection = connect_database()
    cursor = connection.cursor()

    name = (name or "").strip()

    if not name:
        connection.close()
        return False, "empty"

    try:
        cursor.execute(
            "SELECT transaction_type FROM category_groups WHERE group_id = ?",
            (group_id,)
        )

        group = cursor.fetchone()

        if group is None:
            return False, "group_not_found"

        transaction_type = group[0]

        if category_name_exists_for_type(cursor, name, transaction_type):
            return False, "duplicate"

        cursor.execute('''
            INSERT INTO categories (group_id, name)
            VALUES (?, ?)
        ''', (group_id, name))

        connection.commit()
        return True, None

    except sqlite3.Error as e:
        print(e)
        return False, "error"

    finally:
        connection.close()

def update_category(category_id, name):
    connection = connect_database()
    cursor = connection.cursor()

    name = (name or "").strip()

    if not name:
        connection.close()
        return False, "empty"

    try:
        cursor.execute('''
            SELECT category_groups.transaction_type
            FROM categories
            INNER JOIN category_groups
                ON categories.group_id = category_groups.group_id
            WHERE categories.category_id = ?
        ''', (category_id,))

        category = cursor.fetchone()

        if category is None:
            return False, "not_found"

        transaction_type = category[0]

        if category_name_exists_for_type(
            cursor,
            name,
            transaction_type,
            exclude_category_id=category_id
        ):
            return False, "duplicate"

        cursor.execute('''
            UPDATE categories
            SET name = ?
            WHERE category_id = ?
        ''', (name, category_id))

        connection.commit()
        return True, None

    except sqlite3.Error as e:
        print(e)
        return False, "error"

    finally:
        connection.close()

def delete_category(category_id):
    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM transactions WHERE category_id = ?",
            (category_id,)
        )

        transaction_count = cursor.fetchone()[0]

        if transaction_count > 0:
            return False, "referenced"

        cursor.execute(
            "DELETE FROM categories WHERE category_id = ?",
            (category_id,)
        )

        connection.commit()
        return True, None

    except sqlite3.Error as e:
        print(e)
        return False, "error"

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
    categories = [
        CategoryRecord(*row)
        for row in cursor.fetchall()
    ]
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
    categories_by_group = [
        CategoryRecord(*row)
        for row in cursor.fetchall()
    ]
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
    categories_by_type = [
        CategoryRecord(*row)
        for row in cursor.fetchall()
    ]
    connection.close()
    return categories_by_type
