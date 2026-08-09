from datetime import datetime, timezone

from database import migrations
from database.settings_repository import clear_database
from services.backup_exporter import export_backup_document
from services.backup_format import (
    BACKUP_FORMAT_VERSION,
    INTEREST_BACKUP_FORMAT_VERSION,
    PASS_THROUGH_BACKUP_FORMAT_VERSION,
    serialize_backup_document,
)
from services.backup_restorer import restore_backup_json
from services.backup_validator import validate_backup_document


EXPORTED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)


def seed_interest_backup_data():
    connection = migrations.connect_database()
    try:
        connection.executescript(
            """
            INSERT INTO accounts (id, name)
            VALUES (1, 'Bank');

            INSERT INTO category_groups (group_id, name, transaction_type)
            VALUES (1, 'Interest', 'income');

            INSERT INTO categories (category_id, group_id, name)
            VALUES (1, 1, 'Bank interest');

            INSERT INTO transactions (
                id,
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes,
                posting_status
            )
            VALUES (
                10,
                1,
                123,
                1,
                '2026-08-09 12:00:00',
                'Bank interest credit',
                'posted'
            );

            INSERT INTO account_interest_profiles (
                id,
                account_id,
                annual_rate_micros,
                day_count_basis,
                effective_from,
                enabled
            )
            VALUES
                (20, 1, 5000000, 365, '2026-08-08', 1),
                (21, 1, 4750000, 365, '2026-08-10', 1);

            INSERT INTO account_interest_accruals (
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
            )
            VALUES
                (
                    30,
                    1,
                    20,
                    '2026-08-08',
                    1000000,
                    5000000,
                    365,
                    136,
                    36000000000,
                    'reconciled',
                    10
                ),
                (
                    31,
                    1,
                    21,
                    '2026-08-10',
                    1000123,
                    4750000,
                    365,
                    130,
                    15342500000,
                    'estimated',
                    NULL
                );
            """
        )
        connection.commit()
    finally:
        connection.close()


def read_interest_rows():
    connection = migrations.connect_database()
    try:
        profiles = connection.execute(
            """
            SELECT
                id,
                account_id,
                annual_rate_micros,
                day_count_basis,
                effective_from,
                enabled
            FROM account_interest_profiles
            ORDER BY id
            """
        ).fetchall()
        accruals = connection.execute(
            """
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
            ORDER BY id
            """
        ).fetchall()
        transaction = connection.execute(
            """
            SELECT id, amount_centavos, notes, posting_status
            FROM transactions
            WHERE id = 10
            """
        ).fetchone()
        foreign_keys = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
    finally:
        connection.close()
    return profiles, accruals, transaction, foreign_keys


def test_format_5_export_preserves_exact_interest_tracking_rows():
    seed_interest_backup_data()

    document = export_backup_document(
        app_version="1.4.0-dev",
        exported_at=EXPORTED_AT,
    )

    assert document["format_version"] == BACKUP_FORMAT_VERSION == (
        INTEREST_BACKUP_FORMAT_VERSION
    ) == 5
    assert document["metadata"]["database_version"] == 10
    assert document["metadata"]["record_counts"][
        "account_interest_profiles"
    ] == 2
    assert document["metadata"]["record_counts"][
        "account_interest_accruals"
    ] == 2
    assert document["records"]["account_interest_profiles"][0] == {
        "id": 20,
        "account_id": 1,
        "annual_rate_micros": 5000000,
        "day_count_basis": 365,
        "effective_from": "2026-08-08",
        "enabled": 1,
    }
    assert document["records"]["account_interest_accruals"][0][
        "posted_transaction_id"
    ] == 10
    assert document["records"]["account_interest_accruals"][1][
        "accrued_remainder_numerator"
    ] == 15342500000


def test_format_5_clear_restore_round_trip_preserves_interest_and_posted_income():
    seed_interest_backup_data()
    document = export_backup_document(
        app_version="1.4.0-dev",
        exported_at=EXPORTED_AT,
    )
    before = read_interest_rows()

    assert clear_database() is True
    restore_backup_json(serialize_backup_document(document))

    assert read_interest_rows() == before


def test_format_4_normalizes_with_empty_interest_tracking_tables():
    seed_interest_backup_data()
    document = export_backup_document(
        app_version="1.4.0-dev",
        exported_at=EXPORTED_AT,
    )
    document["format_version"] = PASS_THROUGH_BACKUP_FORMAT_VERSION
    document["records"].pop("account_interest_profiles")
    document["records"].pop("account_interest_accruals")
    document["metadata"]["record_counts"].pop(
        "account_interest_profiles"
    )
    document["metadata"]["record_counts"].pop(
        "account_interest_accruals"
    )

    validated = validate_backup_document(document)

    assert validated.document["format_version"] == 5
    assert validated.document["records"]["account_interest_profiles"] == []
    assert validated.document["records"]["account_interest_accruals"] == []


def test_format_5_rejects_broken_interest_relationships():
    seed_interest_backup_data()
    document = export_backup_document(
        app_version="1.4.0-dev",
        exported_at=EXPORTED_AT,
    )
    document["records"]["account_interest_accruals"][0][
        "interest_profile_id"
    ] = 999

    from services.backup_validator import BackupValidationError
    import pytest

    with pytest.raises(BackupValidationError):
        validate_backup_document(document)
