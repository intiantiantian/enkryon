import sqlite3

import pytest

from database import migrations, transfer_repository
from database.account_repository import insert_account
from database.records import TransferRecord
from database.transfer_repository import (
    delete_transfer,
    get_transfer_by_id,
    get_transfers,
    insert_transfer,
    restore_transfer,
    update_transfer,
)


def create_accounts():
    insert_account("Cash")
    insert_account("Bank")
    insert_account("Savings")


def test_migration_7_defaults_existing_transfers_to_internal():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        migrations.create_accounts_table(connection)
        connection.execute("INSERT INTO accounts (name) VALUES ('Cash')")
        connection.execute("INSERT INTO accounts (name) VALUES ('Bank')")
        migrations.create_account_transfers_table(connection)
        connection.execute(
            """
            INSERT INTO account_transfers (
                id,
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                notes
            )
            VALUES (
                7,
                1,
                2,
                100025,
                '2026-08-07 08:30:00',
                'Legacy internal transfer'
            )
            """
        )

        migrations.add_transfer_kind_and_counterparty(connection)

        columns = {
            row[1]: row
            for row in connection.execute(
                "PRAGMA table_info(account_transfers)"
            ).fetchall()
        }
        stored = connection.execute(
            """
            SELECT transfer_kind, counterparty
            FROM account_transfers
            WHERE id = 7
            """
        ).fetchone()

        assert columns["transfer_kind"][2] == "TEXT"
        assert columns["transfer_kind"][3] == 1
        assert columns["transfer_kind"][4] == "'internal'"
        assert columns["counterparty"][2] == "TEXT"
        assert columns["counterparty"][3] == 0
        assert stored == ("internal", None)

        connection.execute(
            """
            INSERT INTO account_transfers (
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                transfer_kind,
                counterparty
            )
            VALUES (
                1,
                2,
                50000,
                '2026-08-07 09:00:00',
                'pass_through',
                'Alex'
            )
            """
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO account_transfers (
                    source_account_id,
                    destination_account_id,
                    amount_centavos,
                    date_time,
                    transfer_kind
                )
                VALUES (
                    1,
                    2,
                    100,
                    '2026-08-07 10:00:00',
                    'unknown'
                )
                """
            )

        for invalid_counterparty in ("", "  Alex", "Alex  ", "   "):
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO account_transfers (
                        source_account_id,
                        destination_account_id,
                        amount_centavos,
                        date_time,
                        transfer_kind,
                        counterparty
                    )
                    VALUES (
                        1,
                        2,
                        100,
                        '2026-08-07 10:30:00',
                        'pass_through',
                        ?
                    )
                    """,
                    (invalid_counterparty,),
                )
    finally:
        connection.close()


def test_repository_defaults_legacy_callers_to_internal():
    create_accounts()

    assert insert_transfer(
        1,
        2,
        10025,
        "2026-08-07 11:00:00",
        "Ordinary transfer",
    ) is True

    transfer = get_transfer_by_id(1)

    assert transfer == TransferRecord(
        transfer_id=1,
        source_account_id=1,
        destination_account_id=2,
        amount_centavos=10025,
        date_time="2026-08-07 11:00:00",
        notes="Ordinary transfer",
        source_account_name="Cash",
        destination_account_name="Bank",
        transfer_kind="internal",
        counterparty=None,
    )


def test_repository_persists_pass_through_kind_and_trimmed_counterparty():
    create_accounts()

    assert insert_transfer(
        1,
        2,
        100025,
        "2026-08-07 12:00:00",
        "Cash-out for friend",
        transfer_kind="pass_through",
        counterparty="  Alex Rivera  ",
    ) is True

    transfer = get_transfer_by_id(1)

    assert transfer.transfer_kind == "pass_through"
    assert transfer.counterparty == "Alex Rivera"
    assert transfer.source_account_name == "Cash"
    assert transfer.destination_account_name == "Bank"


def test_repository_normalizes_blank_counterparty_to_none():
    create_accounts()

    assert insert_transfer(
        1,
        2,
        100,
        "2026-08-07 12:30:00",
        None,
        transfer_kind="pass_through",
        counterparty="   ",
    ) is True

    assert get_transfer_by_id(1).counterparty is None


def test_repository_rejects_unknown_kind_and_non_text_counterparty():
    create_accounts()

    assert insert_transfer(
        1,
        2,
        100,
        "2026-08-07 13:00:00",
        None,
        transfer_kind="unknown",
    ) is False
    assert insert_transfer(
        1,
        2,
        100,
        "2026-08-07 13:00:00",
        None,
        transfer_kind="pass_through",
        counterparty=123,
    ) is False
    assert get_transfers() == []


def test_repository_filters_kinds_with_stable_newest_first_order():
    create_accounts()
    insert_transfer(
        1,
        2,
        100,
        "2026-08-07 14:00:00",
        "Internal",
    )
    insert_transfer(
        2,
        3,
        200,
        "2026-08-07 15:00:00",
        "Pass one",
        transfer_kind="pass_through",
        counterparty="Alex",
    )
    insert_transfer(
        1,
        3,
        300,
        "2026-08-07 15:00:00",
        "Pass two",
        transfer_kind="pass_through",
        counterparty="Bea",
    )

    assert [item.transfer_id for item in get_transfers()] == [3, 2, 1]
    assert [
        item.transfer_id
        for item in get_transfers(transfer_kind="pass_through")
    ] == [3, 2]
    assert [
        item.transfer_id
        for item in get_transfers(
            account_id=2,
            transfer_kind="pass_through",
        )
    ] == [2]
    assert [
        item.transfer_id
        for item in get_transfers(transfer_kind="internal")
    ] == [1]


def test_update_delete_and_restore_preserve_pass_through_metadata():
    create_accounts()
    insert_transfer(
        1,
        2,
        100025,
        "2026-08-07 16:00:00",
        "Original",
        transfer_kind="pass_through",
        counterparty="Alex",
    )

    assert update_transfer(
        source_account_id=2,
        destination_account_id=3,
        amount_centavos=200050,
        date_time="2026-08-07 17:00:00",
        notes="Updated",
        transfer_id=1,
        transfer_kind="pass_through",
        counterparty="  Bea  ",
    ) is True

    updated = get_transfer_by_id(1)
    assert updated.source_account_id == 2
    assert updated.destination_account_id == 3
    assert updated.amount_centavos == 200050
    assert updated.transfer_kind == "pass_through"
    assert updated.counterparty == "Bea"

    assert delete_transfer(1) is True
    assert get_transfer_by_id(1) is None
    assert restore_transfer(updated) is True
    assert get_transfer_by_id(1) == updated


def test_invalid_pass_through_update_leaves_original_record_unchanged():
    create_accounts()
    insert_transfer(
        1,
        2,
        100025,
        "2026-08-07 18:00:00",
        "Original",
        transfer_kind="pass_through",
        counterparty="Alex",
    )
    original = get_transfer_by_id(1)

    assert update_transfer(
        source_account_id=1,
        destination_account_id=2,
        amount_centavos=999,
        date_time="2026-08-07 18:30:00",
        notes="Invalid kind",
        transfer_id=1,
        transfer_kind="invalid",
        counterparty="Bea",
    ) is False
    assert get_transfer_by_id(1) == original


def test_existing_history_index_remains_the_ordering_access_path():
    create_accounts()
    insert_transfer(
        1,
        2,
        100,
        "2026-08-07 19:00:00",
        None,
        transfer_kind="pass_through",
        counterparty="Alex",
    )

    connection = transfer_repository.connect_database()
    try:
        query_plan = connection.execute(
            """
            EXPLAIN QUERY PLAN
            SELECT id
            FROM account_transfers
            ORDER BY date_time DESC, id DESC
            """
        ).fetchall()
        index_names = {
            row[1]
            for row in connection.execute(
                "PRAGMA index_list(account_transfers)"
            ).fetchall()
        }
    finally:
        connection.close()

    details = " ".join(row[3] for row in query_plan)
    assert "account_transfers_history_order_index" in details
    assert "account_transfers_transfer_kind_index" not in index_names
