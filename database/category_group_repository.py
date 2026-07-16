import sqlite3

from .connection import connect_database

def create_category_groups_table(connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = connect_database()

    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                UNIQUE(name, transaction_type)
            )
        ''')

        if owns_connection:
            connection.commit()
    finally:
        if owns_connection:
            connection.close()


def category_group_name_exists(cursor, name, transaction_type, exclude_group_id=None):
    query = '''
        SELECT 1
        FROM category_groups
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
        AND transaction_type = ?
    '''

    params = [name, transaction_type]

    if exclude_group_id is not None:
        query += ' AND group_id != ?'
        params.append(exclude_group_id)

    cursor.execute(query, tuple(params))
    return cursor.fetchone() is not None


def insert_category_group(name, transaction_type):
    connection = connect_database()
    cursor = connection.cursor()

    name = (name or "").strip()

    if not name:
        connection.close()
        return False, "empty"

    if transaction_type not in {"income", "expense"}:
        connection.close()
        return False, "invalid_type"

    try:
        if category_group_name_exists(cursor, name, transaction_type):
            return False, "duplicate"

        cursor.execute('''
            INSERT INTO category_groups (name, transaction_type)
            VALUES (?, ?)
        ''', (name, transaction_type))

        connection.commit()
        return True, None

    except sqlite3.Error as e:
        print(e)
        return False, "error"

    finally:
        connection.close()


def update_category_group(group_id, name):
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
            return False, "not_found"

        transaction_type = group[0]

        if category_group_name_exists(
            cursor,
            name,
            transaction_type,
            exclude_group_id=group_id
        ):
            return False, "duplicate"

        cursor.execute('''
            UPDATE category_groups
            SET name = ?
            WHERE group_id = ?
        ''', (name, group_id))

        connection.commit()
        return True, None

    except sqlite3.Error as e:
        print(e)
        return False, "error"

    finally:
        connection.close()


def delete_category_group(group_id):
    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM categories WHERE group_id = ?",
            (group_id,)
        )

        category_count = cursor.fetchone()[0]

        if category_count > 0:
            return False, "has_categories"

        cursor.execute(
            "DELETE FROM category_groups WHERE group_id = ?",
            (group_id,)
        )

        connection.commit()
        return True, None

    except sqlite3.Error as e:
        print(e)
        return False, "error"

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