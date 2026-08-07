import sqlite3

from database import migrations
from database.account_repository import insert_account
from database.transaction_repository import get_current_balance_centavos
from database.transfer_repository import insert_transfer, update_transfer


def create_accounts():
    assert insert_account("Cash") is True
    assert insert_account("Bank") is True


def test_pass_through_never_changes_either_account_balance():
    create_accounts()
    assert insert_transfer(
        1, 2, 100_000, "2026-08-08 00:10:00", "Friend cash-out",
        transfer_kind="pass_through", counterparty="Alex",
    ) is True

    assert get_current_balance_centavos(1) == 0
    assert get_current_balance_centavos(2) == 0
    assert get_current_balance_centavos() == 0


def test_internal_transfer_keeps_released_balance_behavior():
    create_accounts()
    assert insert_transfer(
        1, 2, 25_050, "2026-08-08 00:20:00", "Own money",
    ) is True

    assert get_current_balance_centavos(1) == -25_050
    assert get_current_balance_centavos(2) == 25_050
    assert get_current_balance_centavos() == 0


def test_editing_pass_through_remains_balance_neutral():
    create_accounts()
    assert insert_transfer(
        1, 2, 50_000, "2026-08-08 00:30:00", None,
        transfer_kind="pass_through",
    ) is True
    assert update_transfer(
        2, 1, 175_025, "2026-08-08 00:35:00", "Edited", 1,
        transfer_kind="pass_through", counterparty="Alex",
    ) is True

    assert get_current_balance_centavos(1) == 0
    assert get_current_balance_centavos(2) == 0


def test_converting_internal_to_pass_through_removes_balance_effect():
    create_accounts()
    assert insert_transfer(
        1, 2, 100_000, "2026-08-08 00:40:00", None,
    ) is True
    assert get_current_balance_centavos(1) == -100_000
    assert get_current_balance_centavos(2) == 100_000

    assert update_transfer(
        1, 2, 100_000, "2026-08-08 00:40:00", None, 1,
        transfer_kind="pass_through", counterparty="Alex",
    ) is True
    assert get_current_balance_centavos(1) == 0
    assert get_current_balance_centavos(2) == 0


def test_converting_pass_through_to_internal_applies_internal_effect():
    create_accounts()
    assert insert_transfer(
        1, 2, 100_000, "2026-08-08 00:50:00", None,
        transfer_kind="pass_through",
    ) is True
    assert update_transfer(
        1, 2, 100_000, "2026-08-08 00:50:00", None, 1,
        transfer_kind="internal",
    ) is True

    assert get_current_balance_centavos(1) == -100_000
    assert get_current_balance_centavos(2) == 100_000


def test_migration_9_removes_temporary_movement_artifacts_and_keeps_parent():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        migrations.create_accounts_table(connection)
        connection.execute("INSERT INTO accounts VALUES (1, 'Cash')")
        connection.execute("INSERT INTO accounts VALUES (2, 'Bank')")
        migrations.create_account_transfers_table(connection)
        migrations.add_transfer_kind_and_counterparty(connection)
        connection.execute(
            """
            INSERT INTO account_transfers (
                id, source_account_id, destination_account_id,
                amount_centavos, date_time, transfer_kind, counterparty
            )
            VALUES (
                7, 1, 2, 100000, '2026-08-08 01:00:00',
                'pass_through', 'Alex'
            )
            """
        )
        migrations.add_pass_through_movements(connection)
        assert connection.execute(
            "SELECT COUNT(*) FROM pass_through_movements"
        ).fetchone()[0] == 2

        migrations.remove_pass_through_movements(connection)
        table = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'pass_through_movements'
            """
        ).fetchone()
        triggers = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'trigger'
              AND name LIKE 'pass_through_movements_%'
            """
        ).fetchall()
        parent = connection.execute(
            """
            SELECT id, transfer_kind, counterparty
            FROM account_transfers WHERE id = 7
            """
        ).fetchone()
    finally:
        connection.close()

    assert table is None
    assert triggers == []
    assert parent == (7, "pass_through", "Alex")
