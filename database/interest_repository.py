import sqlite3
from datetime import date, timedelta

from .connection import connect_database, managed_connection
from .records import InterestAccrualRecord, InterestProfileRecord


EXACT_ACCRUAL_DENOMINATOR = 36_500_000_000


PROFILE_SELECT = '''
    SELECT
        id,
        account_id,
        annual_rate_micros,
        day_count_basis,
        effective_from,
        enabled
    FROM account_interest_profiles
'''


ACCRUAL_SELECT = '''
    SELECT
        id,
        account_id,
        interest_profile_id,
        accrual_date,
        closing_balance_centavos,
        annual_rate_micros,
        day_count_basis,
        accrued_whole_centavos,
        accrued_remainder_numerator,
        status,
        posted_transaction_id
    FROM account_interest_accruals
'''


def create_interest_tables(connection=None):
    owns_connection = connection is None

    if owns_connection:
        connection = connect_database()

    try:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS account_interest_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                annual_rate_micros INTEGER NOT NULL
                    CHECK (
                        typeof(annual_rate_micros) = 'integer'
                        AND annual_rate_micros >= 0
                    ),
                day_count_basis INTEGER NOT NULL DEFAULT 365
                    CHECK (day_count_basis = 365),
                effective_from TEXT NOT NULL
                    CHECK (
                        date(effective_from) IS NOT NULL
                        AND effective_from = date(effective_from)
                    ),
                enabled INTEGER NOT NULL DEFAULT 1
                    CHECK (enabled IN (0, 1)),

                UNIQUE (account_id, effective_from),
                UNIQUE (id, account_id),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        connection.execute('''
            CREATE INDEX IF NOT EXISTS
                account_interest_profiles_effective_index
            ON account_interest_profiles (
                account_id,
                effective_from DESC,
                id DESC
            )
        ''')

        connection.execute(f'''
            CREATE TABLE IF NOT EXISTS account_interest_accruals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                interest_profile_id INTEGER NOT NULL,
                accrual_date TEXT NOT NULL
                    CHECK (
                        date(accrual_date) IS NOT NULL
                        AND accrual_date = date(accrual_date)
                    ),
                closing_balance_centavos INTEGER NOT NULL
                    CHECK (typeof(closing_balance_centavos) = 'integer'),
                annual_rate_micros INTEGER NOT NULL
                    CHECK (
                        typeof(annual_rate_micros) = 'integer'
                        AND annual_rate_micros >= 0
                    ),
                day_count_basis INTEGER NOT NULL DEFAULT 365
                    CHECK (day_count_basis = 365),
                accrued_whole_centavos INTEGER NOT NULL
                    CHECK (
                        typeof(accrued_whole_centavos) = 'integer'
                        AND accrued_whole_centavos >= 0
                    ),
                accrued_remainder_numerator INTEGER NOT NULL
                    CHECK (
                        typeof(accrued_remainder_numerator) = 'integer'
                        AND accrued_remainder_numerator >= 0
                        AND accrued_remainder_numerator <
                            {EXACT_ACCRUAL_DENOMINATOR}
                    ),
                status TEXT NOT NULL DEFAULT 'estimated'
                    CHECK (status IN ('estimated', 'reconciled', 'ignored')),
                posted_transaction_id INTEGER,

                UNIQUE (account_id, accrual_date),
                CHECK (
                    (status = 'reconciled' AND posted_transaction_id IS NOT NULL)
                    OR
                    (status != 'reconciled' AND posted_transaction_id IS NULL)
                ),
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                FOREIGN KEY (interest_profile_id, account_id)
                    REFERENCES account_interest_profiles(id, account_id),
                FOREIGN KEY (posted_transaction_id) REFERENCES transactions(id)
            )
        ''')
        connection.execute('''
            CREATE INDEX IF NOT EXISTS
                account_interest_accruals_history_index
            ON account_interest_accruals (
                account_id,
                accrual_date DESC,
                id DESC
            )
        ''')
        connection.execute('''
            CREATE INDEX IF NOT EXISTS
                account_interest_accruals_status_index
            ON account_interest_accruals (
                status,
                accrual_date DESC,
                id DESC
            )
        ''')

        if owns_connection:
            connection.commit()
    finally:
        if owns_connection:
            connection.close()


def insert_interest_profile(
    account_id,
    annual_rate_micros,
    effective_from,
    enabled=True,
):
    if type(enabled) is not bool:
        return False

    try:
        with managed_connection() as connection:
            cursor = connection.execute(
                '''
                INSERT INTO account_interest_profiles (
                    account_id,
                    annual_rate_micros,
                    day_count_basis,
                    effective_from,
                    enabled
                )
                VALUES (?, ?, 365, ?, ?)
                ''',
                (
                    account_id,
                    annual_rate_micros,
                    effective_from,
                    int(bool(enabled)),
                ),
            )
            connection.commit()
            return cursor.lastrowid
    except (sqlite3.Error, TypeError, ValueError, OverflowError):
        return False


def get_interest_profiles(account_id):
    with managed_connection() as connection:
        rows = connection.execute(
            PROFILE_SELECT
            + '''
                WHERE account_id = ?
                ORDER BY effective_from ASC, id ASC
            ''',
            (account_id,),
        ).fetchall()

    return [InterestProfileRecord(*row) for row in rows]


def get_interest_profile_by_id(profile_id):
    with managed_connection() as connection:
        row = connection.execute(
            PROFILE_SELECT + " WHERE id = ?",
            (profile_id,),
        ).fetchone()

    if row is None:
        return None

    return InterestProfileRecord(*row)


def get_effective_interest_profile(account_id, accrual_date):
    with managed_connection() as connection:
        row = connection.execute(
            PROFILE_SELECT
            + '''
                WHERE account_id = ?
                  AND effective_from <= ?
                ORDER BY effective_from DESC, id DESC
                LIMIT 1
            ''',
            (account_id, accrual_date),
        ).fetchone()

    if row is None:
        return None

    profile = InterestProfileRecord(*row)
    return profile if profile.enabled else None


def delete_interest_profile(profile_id):
    try:
        with managed_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM account_interest_profiles WHERE id = ?",
                (profile_id,),
            )
            if cursor.rowcount == 0:
                return False
            connection.commit()
            return True
    except sqlite3.Error:
        return False



def remove_interest_tracking_data(account_id):
    """Remove all interest-only data for one account atomically.

    Posted transactions created by reconciliation are intentionally preserved.
    Accrual rows are deleted first because they reference profile rows.
    """
    try:
        with managed_connection() as connection:
            profile_count = connection.execute(
                "SELECT COUNT(*) FROM account_interest_profiles WHERE account_id = ?",
                (account_id,),
            ).fetchone()[0]
            if profile_count == 0:
                return (0, 0)

            accrual_cursor = connection.execute(
                "DELETE FROM account_interest_accruals WHERE account_id = ?",
                (account_id,),
            )
            profile_cursor = connection.execute(
                "DELETE FROM account_interest_profiles WHERE account_id = ?",
                (account_id,),
            )
            connection.commit()
            return (profile_cursor.rowcount, accrual_cursor.rowcount)
    except sqlite3.Error:
        return False

def insert_interest_accrual(
    account_id,
    interest_profile_id,
    accrual_date,
    closing_balance_centavos,
    annual_rate_micros,
    accrued_whole_centavos,
    accrued_remainder_numerator,
    status="estimated",
    posted_transaction_id=None,
):
    try:
        with managed_connection() as connection:
            profile = connection.execute(
                '''
                SELECT account_id, annual_rate_micros, day_count_basis
                FROM account_interest_profiles
                WHERE id = ?
                ''',
                (interest_profile_id,),
            ).fetchone()

            if profile != (account_id, annual_rate_micros, 365):
                return False

            cursor = connection.execute(
                '''
                INSERT INTO account_interest_accruals (
                    account_id,
                    interest_profile_id,
                    accrual_date,
                    closing_balance_centavos,
                    annual_rate_micros,
                    day_count_basis,
                    accrued_whole_centavos,
                    accrued_remainder_numerator,
                    status,
                    posted_transaction_id
                )
                VALUES (?, ?, ?, ?, ?, 365, ?, ?, ?, ?)
                ''',
                (
                    account_id,
                    interest_profile_id,
                    accrual_date,
                    closing_balance_centavos,
                    annual_rate_micros,
                    accrued_whole_centavos,
                    accrued_remainder_numerator,
                    status,
                    posted_transaction_id,
                ),
            )
            connection.commit()
            return cursor.lastrowid
    except (sqlite3.Error, OverflowError):
        return False



def get_posted_closing_balance_centavos(account_id, closing_date):
    try:
        closing_date = date.fromisoformat(closing_date)
        cutoff_exclusive = (closing_date + timedelta(days=1)).isoformat()
        cutoff_exclusive += " 00:00:00"

        with managed_connection() as connection:
            transaction_row = connection.execute(
                """
                SELECT COALESCE(
                    SUM(
                        CASE category_groups.transaction_type
                            WHEN 'income' THEN transactions.amount_centavos
                            WHEN 'expense' THEN -transactions.amount_centavos
                            ELSE 0
                        END
                    ),
                    0
                )
                FROM transactions
                INNER JOIN categories
                    ON transactions.category_id = categories.category_id
                INNER JOIN category_groups
                    ON categories.group_id = category_groups.group_id
                WHERE transactions.account_id = ?
                  AND transactions.posting_status = 'posted'
                  AND transactions.date_time < ?
                """,
                (account_id, cutoff_exclusive),
            ).fetchone()

            transfer_row = connection.execute(
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
                  AND date_time < ?
                  AND (
                      source_account_id = ?
                      OR destination_account_id = ?
                  )
                """,
                (
                    account_id,
                    account_id,
                    cutoff_exclusive,
                    account_id,
                    account_id,
                ),
            ).fetchone()

        return int(transaction_row[0]) + int(transfer_row[0])
    except (sqlite3.Error, TypeError, ValueError, OverflowError):
        return False

def get_interest_accrual(account_id, accrual_date):
    with managed_connection() as connection:
        row = connection.execute(
            ACCRUAL_SELECT
            + " WHERE account_id = ? AND accrual_date = ?",
            (account_id, accrual_date),
        ).fetchone()

    if row is None:
        return None

    return InterestAccrualRecord(*row)


def get_interest_accruals(account_id, status=None):
    with managed_connection() as connection:
        query = ACCRUAL_SELECT + " WHERE account_id = ?"
        params = [account_id]

        if status is not None:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY accrual_date ASC, id ASC"
        rows = connection.execute(query, tuple(params)).fetchall()

    return [InterestAccrualRecord(*row) for row in rows]


def update_interest_accrual_status(
    accrual_id,
    status,
    posted_transaction_id=None,
):
    try:
        with managed_connection() as connection:
            cursor = connection.execute(
                '''
                UPDATE account_interest_accruals
                SET status = ?, posted_transaction_id = ?
                WHERE id = ?
                ''',
                (status, posted_transaction_id, accrual_id),
            )
            if cursor.rowcount == 0:
                return False
            connection.commit()
            return True
    except sqlite3.Error:
        return False


def delete_interest_accrual(accrual_id):
    try:
        with managed_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM account_interest_accruals WHERE id = ?",
                (accrual_id,),
            )
            if cursor.rowcount == 0:
                return False
            connection.commit()
            return True
    except sqlite3.Error:
        return False


def get_reconcilable_interest_accruals(account_id, through_date):
    with managed_connection() as connection:
        rows = connection.execute(
            ACCRUAL_SELECT
            + '''
                WHERE account_id = ?
                  AND status = 'estimated'
                  AND accrual_date <= ?
                ORDER BY accrual_date ASC, id ASC
            ''',
            (account_id, through_date),
        ).fetchall()

    return [InterestAccrualRecord(*row) for row in rows]


def reconcile_interest_accruals_transaction(
    *,
    account_id,
    through_date,
    amount_centavos,
    category_id,
    credit_date_time,
    notes,
):
    if type(amount_centavos) is not int or amount_centavos <= 0:
        return False

    try:
        with managed_connection() as connection:
            account = connection.execute(
                "SELECT id FROM accounts WHERE id = ?",
                (account_id,),
            ).fetchone()
            if account is None:
                return False

            category = connection.execute(
                '''
                SELECT category_groups.transaction_type
                FROM categories
                INNER JOIN category_groups
                    ON categories.group_id = category_groups.group_id
                WHERE categories.category_id = ?
                ''',
                (category_id,),
            ).fetchone()
            if category is None or category[0] != "income":
                return False

            rows = connection.execute(
                '''
                SELECT id
                FROM account_interest_accruals
                WHERE account_id = ?
                  AND status = 'estimated'
                  AND accrual_date <= ?
                ORDER BY accrual_date ASC, id ASC
                ''',
                (account_id, through_date),
            ).fetchall()
            accrual_ids = [row[0] for row in rows]
            if not accrual_ids:
                return False

            cursor = connection.execute(
                '''
                INSERT INTO transactions (
                    account_id,
                    amount_centavos,
                    category_id,
                    date_time,
                    notes,
                    posting_status
                )
                VALUES (?, ?, ?, ?, ?, 'posted')
                ''',
                (
                    account_id,
                    amount_centavos,
                    category_id,
                    credit_date_time,
                    notes,
                ),
            )
            transaction_id = cursor.lastrowid

            placeholders = ", ".join("?" for _ in accrual_ids)
            cursor = connection.execute(
                f'''
                UPDATE account_interest_accruals
                SET status = 'reconciled',
                    posted_transaction_id = ?
                WHERE id IN ({placeholders})
                  AND status = 'estimated'
                ''',
                (transaction_id, *accrual_ids),
            )
            if cursor.rowcount != len(accrual_ids):
                raise sqlite3.IntegrityError(
                    "Interest reconciliation changed concurrently."
                )

            connection.commit()
            return transaction_id, len(accrual_ids)
    except (sqlite3.Error, TypeError, ValueError, OverflowError):
        return False
