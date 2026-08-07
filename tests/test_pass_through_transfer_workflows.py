from unittest.mock import Mock

import pytest

from database.account_repository import insert_account
from database.category_group_repository import insert_category_group
from database.category_repository import insert_category
from database.transaction_repository import (
    get_current_balance_centavos,
    get_total_centavos,
    insert_transaction,
)
from database.transfer_repository import get_transfer_by_id, get_transfers
from services import transfer_services


def seed_accounts_and_posted_totals():
    assert insert_account("Cash") is True
    assert insert_account("Bank") is True
    assert insert_account("Wallet") is True
    assert insert_category_group("Salary", "income") == (True, None)
    assert insert_category_group("Food", "expense") == (True, None)
    assert insert_category(1, "Paycheck") == (True, None)
    assert insert_category(2, "Lunch") == (True, None)
    assert insert_transaction(
        1,
        200_000,
        1,
        "2026-08-01 09:00:00",
        None,
    ) is True
    assert insert_transaction(
        1,
        5_000,
        2,
        "2026-08-01 10:00:00",
        None,
    ) is True


def save_pass_through(**overrides):
    arguments = {
        "source_account_id": 1,
        "destination_account_id": 2,
        "amount": "1000.25",
        "date_label": "2026-08-07",
        "time_label": "07:30 PM",
        "notes_label": "Cash-out for friend",
        "transfer_kind": "pass_through",
        "counterparty": "  Alex Rivera  ",
    }
    arguments.update(overrides)
    return transfer_services.save_transfer(**arguments)


def snapshot_financials():
    return {
        "all": get_current_balance_centavos(),
        "cash": get_current_balance_centavos(1),
        "bank": get_current_balance_centavos(2),
        "wallet": get_current_balance_centavos(3),
        "income": get_total_centavos("income"),
        "expense": get_total_centavos("expense"),
    }


def test_pass_through_create_moves_only_the_two_accounts():
    seed_accounts_and_posted_totals()
    before = snapshot_financials()

    result = save_pass_through()

    assert result == transfer_services.TransferSaveResult(
        True,
        "Transfer added successfully.",
    )
    transfer = get_transfer_by_id(1)
    assert transfer.transfer_kind == "pass_through"
    assert transfer.counterparty == "Alex Rivera"
    assert transfer.amount_centavos == 100_025

    after = snapshot_financials()
    assert after["cash"] == before["cash"] - 100_025
    assert after["bank"] == before["bank"] + 100_025
    assert after["wallet"] == before["wallet"]
    assert after["all"] == before["all"]
    assert after["income"] == before["income"]
    assert after["expense"] == before["expense"]


def test_pass_through_preserves_one_centavo_exactly():
    seed_accounts_and_posted_totals()

    result = save_pass_through(amount="0.01")

    assert result.success is True
    transfer = get_transfer_by_id(1)
    assert transfer.amount_centavos == 1
    assert get_current_balance_centavos(1) == 194_999
    assert get_current_balance_centavos(2) == 1


def test_pass_through_edit_reverses_old_effect_before_new_effect():
    seed_accounts_and_posted_totals()
    assert save_pass_through(amount="100.00").success is True

    result = save_pass_through(
        transfer_id=1,
        source_account_id=2,
        destination_account_id=3,
        amount="40.50",
        counterparty="  Bea Santos ",
        notes_label="Updated cash-out",
    )

    assert result == transfer_services.TransferSaveResult(
        True,
        "Transfer updated successfully.",
    )
    transfer = get_transfer_by_id(1)
    assert transfer.source_account_id == 2
    assert transfer.destination_account_id == 3
    assert transfer.amount_centavos == 4_050
    assert transfer.transfer_kind == "pass_through"
    assert transfer.counterparty == "Bea Santos"
    assert get_current_balance_centavos(1) == 195_000
    assert get_current_balance_centavos(2) == -4_050
    assert get_current_balance_centavos(3) == 4_050
    assert get_current_balance_centavos() == 195_000
    assert get_total_centavos("income") == 200_000
    assert get_total_centavos("expense") == 5_000


def test_pass_through_delete_and_restore_reverse_and_reapply_together():
    seed_accounts_and_posted_totals()
    assert save_pass_through(amount="250.75").success is True
    created = get_transfer_by_id(1)
    with_transfer = snapshot_financials()

    deleted = transfer_services.delete_transfer_by_id(1)

    assert deleted.success is True
    assert deleted.deleted_transfer == created
    assert get_transfer_by_id(1) is None
    assert get_current_balance_centavos(1) == 195_000
    assert get_current_balance_centavos(2) == 0
    assert get_current_balance_centavos() == 195_000

    restored = transfer_services.restore_deleted_transfer(
        deleted.deleted_transfer
    )

    assert restored == transfer_services.TransferRestoreResult(
        True,
        "Transfer restored.",
    )
    assert get_transfer_by_id(1) == created
    assert snapshot_financials() == with_transfer


def test_failed_pass_through_update_leaves_original_effect_unchanged(
    monkeypatch,
):
    seed_accounts_and_posted_totals()
    assert save_pass_through(amount="300.00").success is True
    before = snapshot_financials()
    original = get_transfer_by_id(1)
    monkeypatch.setattr(
        transfer_services,
        "update_transfer",
        Mock(return_value=False),
    )

    result = save_pass_through(
        transfer_id=1,
        source_account_id=2,
        destination_account_id=3,
        amount="10.00",
    )

    assert result == transfer_services.TransferSaveResult(
        False,
        "Transfer could not be updated.",
    )
    assert get_transfer_by_id(1) == original
    assert snapshot_financials() == before


@pytest.mark.parametrize("invalid_kind", ["temporary", "income", "", None, []])
def test_pass_through_service_rejects_invalid_transfer_kind(
    monkeypatch,
    invalid_kind,
):
    insert_transfer = Mock()
    monkeypatch.setattr(
        transfer_services,
        "insert_transfer",
        insert_transfer,
    )

    result = transfer_services.save_transfer(
        source_account_id=1,
        destination_account_id=2,
        amount="1.00",
        date_label="2026-08-07",
        time_label="07:30 PM",
        notes_label="Test",
        transfer_kind=invalid_kind,
        counterparty="Alex",
    )

    assert result == transfer_services.TransferSaveResult(
        False,
        "Please select a valid transfer type.",
    )
    insert_transfer.assert_not_called()


def test_pass_through_service_rejects_non_text_counterparty(monkeypatch):
    insert_transfer = Mock()
    monkeypatch.setattr(
        transfer_services,
        "insert_transfer",
        insert_transfer,
    )

    result = transfer_services.save_transfer(
        source_account_id=1,
        destination_account_id=2,
        amount="1.00",
        date_label="2026-08-07",
        time_label="07:30 PM",
        notes_label="Test",
        transfer_kind="pass_through",
        counterparty=123,
    )

    assert result == transfer_services.TransferSaveResult(
        False,
        "Please enter a valid counterparty.",
    )
    insert_transfer.assert_not_called()


def test_pass_through_service_rejects_same_account_before_database_access(
    monkeypatch,
):
    get_account_by_id = Mock()
    insert_transfer = Mock()
    monkeypatch.setattr(
        transfer_services,
        "get_account_by_id",
        get_account_by_id,
    )
    monkeypatch.setattr(
        transfer_services,
        "insert_transfer",
        insert_transfer,
    )

    result = save_pass_through(
        source_account_id=1,
        destination_account_id=1,
    )

    assert result == transfer_services.TransferSaveResult(
        False,
        "Source and destination accounts must be different.",
    )
    get_account_by_id.assert_not_called()
    insert_transfer.assert_not_called()


def test_internal_transfer_service_remains_default_and_backward_compatible():
    seed_accounts_and_posted_totals()

    result = transfer_services.save_transfer(
        source_account_id=1,
        destination_account_id=2,
        amount="10.00",
        date_label="2026-08-07",
        time_label="07:30 PM",
        notes_label="Savings",
    )

    assert result.success is True
    transfer = get_transfer_by_id(1)
    assert transfer.transfer_kind == "internal"
    assert transfer.counterparty is None
    assert get_transfers(transfer_kind="pass_through") == []
    assert get_transfers(transfer_kind="internal") == [transfer]
