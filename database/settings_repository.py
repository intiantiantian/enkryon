from .connection import connect_database

def clear_database():
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM categories")
    cursor.execute("DELETE FROM category_groups")
    cursor.execute("DELETE FROM accounts")

    conn.commit()
    conn.close()