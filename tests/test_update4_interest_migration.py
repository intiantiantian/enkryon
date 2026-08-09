import sqlite3

import pytest

from database import migrations
from database.interest_repository import EXACT_ACCRUAL_DENOMINATOR


def test_migration_10_creates_constrained_interest_schema():
    connection = migrations.connect_database()
    try:
        migration = connection.execute(
            "SELECT name FROM schema_migrations WHERE version = 10"
        ).fetchone()
        profile_columns = {
            row[1]: row[2]
            for row in connection.execute(
                "PRAGMA table_info(account_interest_profiles)"
            ).fetchall()
        }
        accrual_columns = {
            row[1]: row[2]
            for row in connection.execute(
                "PRAGMA table_info(account_interest_accruals)"
            ).fetchall()
        }
        indexes = {
            row[1]
            for table in (
                "account_interest_profiles",
                "account_interest_accruals",
            )
            for row in connection.execute(
                f"PRAGMA index_list({table})"
            ).fetchall()
        }
    finally:
        connection.close()

    assert migration == ("daily_bank_interest",)
    assert profile_columns == {
        "id": "INTEGER",
        "account_id": "INTEGER",
        "annual_rate_micros": "INTEGER",
        "day_count_basis": "INTEGER",
        "effective_from": "TEXT",
        "enabled": "INTEGER",
    }
    assert accrual_columns == {
        "id": "INTEGER",
        "account_id": "INTEGER",
        "interest_profile_id": "INTEGER",
        "accrual_date": "TEXT",
        "closing_balance_centavos": "INTEGER",
        "annual_rate_micros": "INTEGER",
        "day_count_basis": "INTEGER",
        "accrued_whole_centavos": "INTEGER",
        "accrued_remainder_numerator": "INTEGER",
        "status": "TEXT",
        "posted_transaction_id": "INTEGER",
    }
    assert "account_interest_profiles_effective_index" in indexes
    assert "account_interest_accruals_history_index" in indexes
    assert "account_interest_accruals_status_index" in indexes


def test_interest_schema_enforces_actual_365_and_exact_remainder_range():
    connection = migrations.connect_database()
    try:
        connection.execute("INSERT INTO accounts (name) VALUES ('Savings')")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                INSERT INTO account_interest_profiles (
                    account_id, annual_rate_micros, day_count_basis,
                    effective_from, enabled
                ) VALUES (1, 1000000, 360, '2026-08-01', 1)
                '''
            )
        connection.execute(
            '''
            INSERT INTO account_interest_profiles (
                account_id, annual_rate_micros, day_count_basis,
                effective_from, enabled
            ) VALUES (1, 1000000, 365, '2026-08-01', 1)
            '''
        )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                INSERT INTO account_interest_accruals (
                    account_id, interest_profile_id, accrual_date,
                    closing_balance_centavos, annual_rate_micros,
                    day_count_basis, accrued_whole_centavos,
                    accrued_remainder_numerator, status
                ) VALUES (1, 1, '2026-08-02', 10000, 1000000, 365, 0, ?, 'estimated')
                ''',
                (EXACT_ACCRUAL_DENOMINATOR,),
            )
    finally:
        connection.close()


def test_migration_10_is_empty_for_existing_financial_ledgers():
    connection = migrations.connect_database()
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM account_interest_profiles"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM account_interest_accruals"
        ).fetchone()[0] == 0
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connection.close()
