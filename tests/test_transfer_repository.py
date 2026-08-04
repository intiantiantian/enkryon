import pytest

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


def create_transfer_test_accounts():
    insert_account("Cash")
    insert_account("Savings")
    insert_account("Emergency Fund")


def test_insert_transfer_and_get_by_id():
    create_transfer_test_accounts()

    result = insert_transfer(
        source_account_id=1,
        destination_account_id=2,
        amount_centavos=10025,
        date_time="2026-08-04 14:30:00",
        notes="Emergency fund",
    )

    transfer = get_transfer_by_id(1)

    assert result is True
    assert isinstance(transfer, TransferRecord)
    assert transfer == TransferRecord(
        transfer_id=1,
        source_account_id=1,
        destination_account_id=2,
        amount_centavos=10025,
        date_time="2026-08-04 14:30:00",
        notes="Emergency fund",
        source_account_name="Cash",
        destination_account_name="Savings",
    )


def test_get_transfer_by_id_returns_none_when_missing():
    assert get_transfer_by_id(999) is None


def test_get_transfers_orders_newest_first_with_stable_id_tie_breaker():
    create_transfer_test_accounts()
    insert_transfer(1, 2, 100, "2026-08-04 08:00:00", "First")
    insert_transfer(2, 3, 200, "2026-08-04 09:00:00", "Second")
    insert_transfer(1, 3, 300, "2026-08-04 09:00:00", "Third")

    assert [
        transfer.transfer_id
        for transfer in get_transfers()
    ] == [3, 2, 1]


def test_get_transfers_filters_either_account_direction():
    create_transfer_test_accounts()
    insert_transfer(1, 2, 100, "2026-08-04 08:00:00", "Incoming")
    insert_transfer(2, 3, 200, "2026-08-04 09:00:00", "Outgoing")
    insert_transfer(1, 3, 300, "2026-08-04 10:00:00", "Unrelated")

    transfers = get_transfers(account_id=2)

    assert [
        transfer.transfer_id
        for transfer in transfers
    ] == [2, 1]
    assert transfers[0].source_account_name == "Savings"
    assert transfers[1].destination_account_name == "Savings"


def test_get_transfers_can_limit_results():
    create_transfer_test_accounts()
    insert_transfer(1, 2, 100, "2026-08-04 08:00:00", None)
    insert_transfer(2, 3, 200, "2026-08-04 09:00:00", None)
    insert_transfer(1, 3, 300, "2026-08-04 10:00:00", None)

    assert [
        transfer.transfer_id
        for transfer in get_transfers(limit=2)
    ] == [3, 2]


def test_update_transfer_changes_every_editable_field():
    create_transfer_test_accounts()
    insert_transfer(
        1,
        2,
        10025,
        "2026-08-04 14:30:00",
        "Original",
    )

    result = update_transfer(
        source_account_id=2,
        destination_account_id=3,
        amount_centavos=20050,
        date_time="2026-08-05 09:45:00",
        notes=None,
        transfer_id=1,
    )

    assert result is True
    assert get_transfer_by_id(1) == TransferRecord(
        transfer_id=1,
        source_account_id=2,
        destination_account_id=3,
        amount_centavos=20050,
        date_time="2026-08-05 09:45:00",
        notes=None,
        source_account_name="Savings",
        destination_account_name="Emergency Fund",
    )


def test_update_transfer_returns_false_when_missing():
    create_transfer_test_accounts()

    assert update_transfer(
        1,
        2,
        100,
        "2026-08-04 14:30:00",
        None,
        999,
    ) is False


def test_invalid_update_rolls_back_without_changing_transfer():
    create_transfer_test_accounts()
    insert_transfer(
        1,
        2,
        10025,
        "2026-08-04 14:30:00",
        "Original",
    )
    original_transfer = get_transfer_by_id(1)

    result = update_transfer(
        source_account_id=2,
        destination_account_id=2,
        amount_centavos=20050,
        date_time="2026-08-05 09:45:00",
        notes="Invalid",
        transfer_id=1,
    )

    assert result is False
    assert get_transfer_by_id(1) == original_transfer


def test_delete_and_restore_transfer_preserve_identity():
    create_transfer_test_accounts()
    insert_transfer(
        1,
        2,
        10025,
        "2026-08-04 14:30:00",
        "Restore me",
    )
    transfer = get_transfer_by_id(1)

    assert delete_transfer(1) is True
    assert get_transfer_by_id(1) is None
    assert restore_transfer(transfer) is True
    assert get_transfer_by_id(1) == transfer


def test_delete_transfer_returns_false_when_missing():
    assert delete_transfer(999) is False


@pytest.mark.parametrize(
    (
        "source_account_id",
        "destination_account_id",
        "amount_centavos",
        "date_time",
    ),
    (
        (1, 1, 100, "2026-08-04 14:30:00"),
        (1, 2, 0, "2026-08-04 14:30:00"),
        (1, 2, -1, "2026-08-04 14:30:00"),
        (1, 2, 1.5, "2026-08-04 14:30:00"),
        (1, 2, 100, "2026-08-04"),
        (999, 2, 100, "2026-08-04 14:30:00"),
        (1, 999, 100, "2026-08-04 14:30:00"),
    ),
)
def test_insert_transfer_rejects_database_constraint_violations(
    source_account_id,
    destination_account_id,
    amount_centavos,
    date_time,
):
    create_transfer_test_accounts()

    result = insert_transfer(
        source_account_id,
        destination_account_id,
        amount_centavos,
        date_time,
        None,
    )

    assert result is False
    assert get_transfers() == []
