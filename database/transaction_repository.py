import sqlite3

from datetime import timedelta

from .connection import connect_database, managed_connection
from .records import TransactionDetailRecord, TransactionListRecord
from .transfer_repository import get_transfer_balance_centavos


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
    posting_status="posted",
):
    try:
        with managed_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO transactions (
                    account_id,
                    amount_centavos,
                    category_id,
                    date_time,
                    notes,
                    posting_status
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes,
                posting_status,
            ))
            connection.commit()
            return True
    except sqlite3.Error:
        return False


def get_transactions(
    limit=None,
    account_id=None,
    transaction_type=None,
    search_text=None,
    group_id=None,
    category_id=None,
    start_date=None,
    end_date=None,
    posting_status=None,
):
    with managed_connection() as connection:
        cursor = connection.cursor()
        query = '''SELECT transactions.id,
                    accounts.name,
                    category_groups.name,
                    categories.name,
                    transactions.amount_centavos,
                    transactions.date_time,
                    transactions.notes,
                    category_groups.transaction_type,
                    transactions.posting_status
                    FROM transactions
                    INNER JOIN accounts
                        ON transactions.account_id = accounts.id
                    INNER JOIN categories
                        ON transactions.category_id = categories.category_id
                    INNER JOIN category_groups
                        ON categories.group_id = category_groups.group_id
                '''

        conditions = []
        params = []

        if search_text:
            escaped_search_text = (
                search_text
                .replace('\\', '\\\\')
                .replace('%', '\\%')
                .replace('_', '\\_')
            )
            search_pattern = f'%{escaped_search_text}%'
            conditions.append(
                '''(
                    COALESCE(transactions.notes, '') LIKE ? ESCAPE '\\'
                    OR accounts.name LIKE ? ESCAPE '\\'
                    OR category_groups.name LIKE ? ESCAPE '\\'
                    OR categories.name LIKE ? ESCAPE '\\'
                )'''
            )
            params.extend([search_pattern] * 4)

        if account_id is not None:
            conditions.append('transactions.account_id = ?')
            params.append(account_id)

        if transaction_type is not None:
            conditions.append('category_groups.transaction_type = ?')
            params.append(transaction_type)

        if group_id is not None:
            conditions.append('categories.group_id = ?')
            params.append(group_id)

        if category_id is not None:
            conditions.append('transactions.category_id = ?')
            params.append(category_id)

        if posting_status is not None:
            conditions.append('transactions.posting_status = ?')
            params.append(posting_status)

        if start_date is not None:
            conditions.append('transactions.date_time >= ?')
            params.append(
                f'{start_date.isoformat()} 00:00:00'
            )

        if end_date is not None:
            end_date_exclusive = end_date + timedelta(days=1)
            conditions.append('transactions.date_time < ?')
            params.append(
                f'{end_date_exclusive.isoformat()} 00:00:00'
            )

        if conditions:
            query += ' WHERE ' + " AND ".join(conditions)

        query += (
            ' ORDER BY transactions.date_time DESC, '
            'transactions.id DESC'
        )

        if limit is not None:
            query += ' LIMIT ?'
            params.append(limit)

        cursor.execute(query, tuple(params))
        return [
            TransactionListRecord(*row)
            for row in cursor.fetchall()
        ]


def get_transaction_by_id(transaction_id):
    with managed_connection() as connection:
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
                       category_groups.transaction_type,
                       transactions.posting_status
                       FROM transactions
                       INNER JOIN accounts
                           ON transactions.account_id = accounts.id
                       INNER JOIN categories
                           ON transactions.category_id = categories.category_id
                       INNER JOIN category_groups
                           ON categories.group_id = category_groups.group_id
                       WHERE transactions.id = ?
                       ''', (transaction_id,))
        row = cursor.fetchone()

    if row is None:
        return None

    return TransactionDetailRecord(*row)


def update_transaction(
    account_id,
    amount_centavos,
    category_id,
    date_time,
    notes,
    transaction_id,
    posting_status=None,
):
    try:
        with managed_connection() as connection:
            assignments = [
                "account_id = ?",
                "amount_centavos = ?",
                "category_id = ?",
                "date_time = ?",
                "notes = ?",
            ]
            params = [
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes,
            ]

            if posting_status is not None:
                assignments.append("posting_status = ?")
                params.append(posting_status)

            params.append(transaction_id)
            query = (
                "UPDATE transactions SET "
                + ", ".join(assignments)
                + " WHERE id = ?"
            )

            cursor = connection.execute(query, tuple(params))

            if cursor.rowcount == 0:
                return False

            connection.commit()
            return True
    except sqlite3.Error:
        return False


def update_transaction_posting_status(
    transaction_id,
    posting_status,
    expected_posting_status=None,
):
    try:
        with managed_connection() as connection:
            query = '''
                UPDATE transactions
                SET posting_status = ?
                WHERE id = ?
            '''
            params = [posting_status, transaction_id]

            if expected_posting_status is not None:
                query += " AND posting_status = ?"
                params.append(expected_posting_status)

            cursor = connection.execute(query, tuple(params))

            if cursor.rowcount == 0:
                return False

            connection.commit()
            return True
    except sqlite3.Error:
        return False


def delete_transaction(transaction_id):
    try:
        with managed_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                'DELETE FROM transactions WHERE id = ?',
                (transaction_id,)
            )

            if cursor.rowcount == 0:
                return False

            connection.commit()
            return True
    except sqlite3.Error:
        return False


def restore_transaction(transaction):
    try:
        with managed_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                '''
                INSERT INTO transactions (
                    id,
                    account_id,
                    amount_centavos,
                    category_id,
                    date_time,
                    notes,
                    posting_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    transaction.transaction_id,
                    transaction.account_id,
                    transaction.amount_centavos,
                    transaction.category_id,
                    transaction.date_time,
                    transaction.notes,
                    transaction.posting_status,
                ),
            )
            connection.commit()
            return True
    except sqlite3.Error:
        return False


def get_total_centavos(transaction_type, account_id=None):
    try:
        with managed_connection() as connection:
            cursor = connection.cursor()
            query = '''
                SELECT SUM(amount_centavos)
                FROM transactions
                INNER JOIN categories
                    ON transactions.category_id = categories.category_id
                INNER JOIN category_groups
                    ON categories.group_id = category_groups.group_id
                WHERE transaction_type = ?
                  AND transactions.posting_status = 'posted'
            '''

            params = [transaction_type]

            if account_id is not None:
                query += " AND transactions.account_id = ?"
                params.append(account_id)

            cursor.execute(query, tuple(params))
            amount_centavos = cursor.fetchone()[0]

            return int(amount_centavos or 0)
    except sqlite3.Error as error:
        return False


def get_current_balance_centavos(account_id=None):
    return (
        get_total_centavos("income", account_id)
        - get_total_centavos("expense", account_id)
        + get_transfer_balance_centavos(account_id)
    )
