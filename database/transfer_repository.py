import sqlite3

from .connection import connect_database, managed_connection
from .records import TransferRecord


TRANSFER_SELECT = '''
    SELECT
        account_transfers.id,
        account_transfers.source_account_id,
        account_transfers.destination_account_id,
        account_transfers.amount_centavos,
        account_transfers.date_time,
        account_transfers.notes,
        source_accounts.name,
        destination_accounts.name,
        account_transfers.transfer_kind,
        account_transfers.counterparty
    FROM account_transfers
    INNER JOIN accounts AS source_accounts
        ON account_transfers.source_account_id = source_accounts.id
    INNER JOIN accounts AS destination_accounts
        ON account_transfers.destination_account_id =
           destination_accounts.id
'''


def create_account_transfers_table(connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = connect_database()

    try:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS account_transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_account_id INTEGER NOT NULL,
                destination_account_id INTEGER NOT NULL,
                amount_centavos INTEGER NOT NULL
                    CHECK (
                        typeof(amount_centavos) = 'integer'
                        AND amount_centavos > 0
                    ),
                date_time TEXT NOT NULL
                    CHECK (
                        strftime(
                            '%Y-%m-%d %H:%M:%S',
                            date_time
                        ) IS NOT NULL
                        AND date_time = strftime(
                            '%Y-%m-%d %H:%M:%S',
                            date_time
                        )
                    ),
                notes TEXT,

                CHECK (source_account_id != destination_account_id),
                FOREIGN KEY (source_account_id) REFERENCES accounts(id),
                FOREIGN KEY (destination_account_id) REFERENCES accounts(id)
            )
        ''')
        connection.execute('''
            CREATE INDEX IF NOT EXISTS account_transfers_history_order_index
            ON account_transfers (date_time DESC, id DESC)
        ''')
        connection.execute('''
            CREATE INDEX IF NOT EXISTS account_transfers_source_history_index
            ON account_transfers (
                source_account_id,
                date_time DESC,
                id DESC
            )
        ''')
        connection.execute('''
            CREATE INDEX IF NOT EXISTS
                account_transfers_destination_history_index
            ON account_transfers (
                destination_account_id,
                date_time DESC,
                id DESC
            )
        ''')

        if owns_connection:
            connection.commit()
    finally:
        if owns_connection:
            connection.close()


def _normalize_counterparty(counterparty):
    if counterparty is None:
        return None

    if not isinstance(counterparty, str):
        raise ValueError("counterparty must be text or None")

    normalized_counterparty = counterparty.strip()
    return normalized_counterparty or None


def insert_transfer(
    source_account_id,
    destination_account_id,
    amount_centavos,
    date_time,
    notes,
    transfer_kind="internal",
    counterparty=None,
):
    try:
        counterparty = _normalize_counterparty(counterparty)
        with managed_connection() as connection:
            connection.execute(
                '''
                INSERT INTO account_transfers (
                    source_account_id,
                    destination_account_id,
                    amount_centavos,
                    date_time,
                    notes,
                    transfer_kind,
                    counterparty
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    source_account_id,
                    destination_account_id,
                    amount_centavos,
                    date_time,
                    notes,
                    transfer_kind,
                    counterparty,
                ),
            )
            connection.commit()
            return True
    except (sqlite3.Error, ValueError):
        return False


def get_transfers(limit=None, account_id=None, transfer_kind=None):
    with managed_connection() as connection:
        query = TRANSFER_SELECT
        params = []

        conditions = []

        if account_id is not None:
            conditions.append(
                "(account_transfers.source_account_id = ? "
                "OR account_transfers.destination_account_id = ?)"
            )
            params.extend((account_id, account_id))

        if transfer_kind is not None:
            conditions.append("account_transfers.transfer_kind = ?")
            params.append(transfer_kind)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += '''
            ORDER BY account_transfers.date_time DESC,
                     account_transfers.id DESC
        '''

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        rows = connection.execute(query, tuple(params)).fetchall()

    return [TransferRecord(*row) for row in rows]


def get_transfer_by_id(transfer_id):
    with managed_connection() as connection:
        row = connection.execute(
            TRANSFER_SELECT + " WHERE account_transfers.id = ?",
            (transfer_id,),
        ).fetchone()

    if row is None:
        return None

    return TransferRecord(*row)


def get_transfer_balance_centavos(account_id=None):
    if account_id is None:
        return 0

    try:
        with managed_connection() as connection:
            internal_row = connection.execute(
                """
                SELECT COALESCE(
                    SUM(
                        CASE
                            WHEN destination_account_id = ?
                                THEN amount_centavos
                            WHEN source_account_id = ?
                                THEN -amount_centavos
                            ELSE 0
                        END
                    ),
                    0
                )
                FROM account_transfers
                WHERE transfer_kind = 'internal'
                  AND (
                      source_account_id = ?
                      OR destination_account_id = ?
                  )
                """,
                (account_id, account_id, account_id, account_id),
            ).fetchone()

            pass_through_row = connection.execute(
                """
                WITH valid_pass_through AS (
                    SELECT account_transfers.id AS transfer_id
                    FROM account_transfers
                    INNER JOIN pass_through_movements
                        ON pass_through_movements.transfer_id =
                           account_transfers.id
                    WHERE account_transfers.transfer_kind = 'pass_through'
                    GROUP BY account_transfers.id
                    HAVING COUNT(*) = 2
                       AND SUM(
                            CASE
                                WHEN
                                    pass_through_movements.direction = 'outflow'
                                    AND pass_through_movements.account_id =
                                        account_transfers.source_account_id
                                    AND pass_through_movements.amount_centavos =
                                        account_transfers.amount_centavos
                                    THEN 1
                                ELSE 0
                            END
                       ) = 1
                       AND SUM(
                            CASE
                                WHEN
                                    pass_through_movements.direction = 'inflow'
                                    AND pass_through_movements.account_id =
                                        account_transfers.destination_account_id
                                    AND pass_through_movements.amount_centavos =
                                        account_transfers.amount_centavos
                                    THEN 1
                                ELSE 0
                            END
                       ) = 1
                )
                SELECT COALESCE(
                    SUM(
                        CASE pass_through_movements.direction
                            WHEN 'inflow'
                                THEN pass_through_movements.amount_centavos
                            ELSE -pass_through_movements.amount_centavos
                        END
                    ),
                    0
                )
                FROM pass_through_movements
                INNER JOIN valid_pass_through
                    ON valid_pass_through.transfer_id =
                       pass_through_movements.transfer_id
                WHERE pass_through_movements.account_id = ?
                """,
                (account_id,),
            ).fetchone()

        return int(internal_row[0]) + int(pass_through_row[0])
    except sqlite3.Error:
        return False

def update_transfer(
    source_account_id,
    destination_account_id,
    amount_centavos,
    date_time,
    notes,
    transfer_id,
    transfer_kind="internal",
    counterparty=None,
):
    try:
        counterparty = _normalize_counterparty(counterparty)
        with managed_connection() as connection:
            cursor = connection.execute(
                '''
                UPDATE account_transfers
                SET source_account_id = ?,
                    destination_account_id = ?,
                    amount_centavos = ?,
                    date_time = ?,
                    notes = ?,
                    transfer_kind = ?,
                    counterparty = ?
                WHERE id = ?
                ''',
                (
                    source_account_id,
                    destination_account_id,
                    amount_centavos,
                    date_time,
                    notes,
                    transfer_kind,
                    counterparty,
                    transfer_id,
                ),
            )

            if cursor.rowcount == 0:
                return False

            connection.commit()
            return True
    except (sqlite3.Error, ValueError):
        return False


def delete_transfer(transfer_id):
    try:
        with managed_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM account_transfers WHERE id = ?",
                (transfer_id,),
            )

            if cursor.rowcount == 0:
                return False

            connection.commit()
            return True
    except sqlite3.Error:
        return False


def restore_transfer(transfer):
    try:
        with managed_connection() as connection:
            connection.execute(
                '''
                INSERT INTO account_transfers (
                    id,
                    source_account_id,
                    destination_account_id,
                    amount_centavos,
                    date_time,
                    notes,
                    transfer_kind,
                    counterparty
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    transfer.transfer_id,
                    transfer.source_account_id,
                    transfer.destination_account_id,
                    transfer.amount_centavos,
                    transfer.date_time,
                    transfer.notes,
                    transfer.transfer_kind,
                    _normalize_counterparty(transfer.counterparty),
                ),
            )
            connection.commit()
            return True
    except (sqlite3.Error, ValueError):
        return False
