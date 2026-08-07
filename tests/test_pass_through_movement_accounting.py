import sqlite3

from database import migrations
from database.account_repository import insert_account
from database.transaction_repository import get_current_balance_centavos
from database.transfer_repository import insert_transfer


def create_accounts():
    assert insert_account("Cash") is True
    assert insert_account("Bank") is True


def read_movements(transfer_id):
    connection = migrations.connect_database()
    try:
        return connection.execute(
            """
            SELECT direction, account_id, amount_centavos
            FROM pass_through_movements
            WHERE transfer_id = ?
            ORDER BY direction
            """,
            (transfer_id,),
        ).fetchall()
    finally:
        connection.close()


def test_pass_through_persists_explicit_outflow_and_inflow():
    create_accounts()
    assert insert_transfer(
        1, 2, 100_025, "2026-08-07 20:00:00", "Cash-out",
        transfer_kind="pass_through", counterparty="Alex",
    ) is True

    assert read_movements(1) == [
        ("inflow", 2, 100_025),
        ("outflow", 1, 100_025),
    ]
    assert get_current_balance_centavos(1) == -100_025
    assert get_current_balance_centavos(2) == 100_025
    assert get_current_balance_centavos() == 0


def test_pass_through_parent_without_movements_is_balance_neutral():
    create_accounts()
    assert insert_transfer(
        1, 2, 100_000, "2026-08-07 20:15:00", "Cash-out",
        transfer_kind="pass_through",
    ) is True

    connection = migrations.connect_database()
    try:
        connection.execute(
            "DELETE FROM pass_through_movements WHERE transfer_id = 1"
        )
        connection.commit()
    finally:
        connection.close()

    assert read_movements(1) == []
    assert get_current_balance_centavos(1) == 0
    assert get_current_balance_centavos(2) == 0
    assert get_current_balance_centavos() == 0


def test_incomplete_pass_through_pair_fails_closed():
    create_accounts()
    assert insert_transfer(
        1, 2, 50_000, "2026-08-07 20:30:00", None,
        transfer_kind="pass_through",
    ) is True

    connection = migrations.connect_database()
    try:
        connection.execute(
            """
            DELETE FROM pass_through_movements
            WHERE transfer_id = 1 AND direction = 'inflow'
            """
        )
        connection.commit()
    finally:
        connection.close()

    assert get_current_balance_centavos(1) == 0
    assert get_current_balance_centavos(2) == 0


def test_internal_transfer_keeps_parent_balance_behavior():
    create_accounts()
    assert insert_transfer(
        1, 2, 25_050, "2026-08-07 20:45:00", "Own money",
    ) is True

    assert read_movements(1) == []
    assert get_current_balance_centavos(1) == -25_050
    assert get_current_balance_centavos(2) == 25_050


def test_migration_8_backfills_development_pass_through_parent():
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
                amount_centavos, date_time, transfer_kind
            )
            VALUES (
                7, 1, 2, 50025,
                '2026-08-07 21:00:00', 'pass_through'
            )
            """
        )
        migrations.add_pass_through_movements(connection)
        rows = connection.execute(
            """
            SELECT transfer_id, direction, account_id, amount_centavos
            FROM pass_through_movements
            ORDER BY direction
            """
        ).fetchall()
    finally:
        connection.close()

    assert rows == [
        (7, "inflow", 2, 50_025),
        (7, "outflow", 1, 50_025),
    ]
