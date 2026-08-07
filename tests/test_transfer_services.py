import sqlite3
from unittest.mock import Mock, call

import pytest

from database.account_repository import insert_account
from database.records import AccountRecord, TransferRecord
from database.transfer_repository import get_transfer_by_id
from services import transfer_services


def make_transfer():
    return TransferRecord(
        transfer_id=17,
        source_account_id=2,
        destination_account_id=3,
        amount_centavos=12345,
        date_time="2026-08-04 19:30:00",
        notes="Emergency fund",
        source_account_name="Cash",
        destination_account_name="Savings",
    )


def make_transfer_arguments(**overrides):
    arguments = {
        "source_account_id": 2,
        "destination_account_id": 3,
        "amount": "123.45",
        "date_label": "2026-08-04",
        "time_label": "07:30 PM",
        "notes_label": "Emergency fund",
    }
    arguments.update(overrides)
    return arguments


def patch_valid_accounts(monkeypatch):
    get_account_by_id = Mock(
        side_effect=[
            AccountRecord(2, "Cash"),
            AccountRecord(3, "Savings"),
        ]
    )
    monkeypatch.setattr(
        transfer_services,
        "get_account_by_id",
        get_account_by_id,
    )
    return get_account_by_id


@pytest.mark.parametrize(
    ("source_id", "destination_id", "amount", "message"),
    [
        (None, 3, "1", "Please select a source account."),
        (2, None, "1", "Please select a destination account."),
        (
            2,
            2,
            "1",
            "Source and destination accounts must be different.",
        ),
        (
            2,
            3,
            "not money",
            "Please enter a valid amount with up to two decimal places.",
        ),
        (
            2,
            3,
            "1.001",
            "Please enter a valid amount with up to two decimal places.",
        ),
        (2, 3, "0", "Amount cannot be less than or equal to zero."),
        (2, 3, "-1", "Amount cannot be less than or equal to zero."),
    ],
)
def test_validate_transfer_form_rejects_invalid_input(
    source_id,
    destination_id,
    amount,
    message,
):
    assert transfer_services.validate_transfer_form(
        source_id,
        destination_id,
        amount,
    ) == (False, message)


@pytest.mark.parametrize("amount", ["0.01", "123.45", 100])
def test_validate_transfer_form_accepts_positive_exact_amounts(amount):
    assert transfer_services.validate_transfer_form(
        2,
        3,
        amount,
    ) == (True, None)


def test_build_transfer_payload_preserves_exact_centavos_and_notes():
    assert transfer_services.build_transfer_payload(
        source_account_id=2,
        destination_account_id=3,
        amount="123.45",
        date_label="2026-08-04",
        time_label="07:30 PM",
        notes_label="Emergency fund",
    ) == {
        "source_account_id": 2,
        "destination_account_id": 3,
        "amount_centavos": 12345,
        "date_time": "2026-08-04 19:30:00",
        "notes": "Emergency fund",
        "transfer_kind": "internal",
        "counterparty": None,
    }


def test_build_transfer_payload_normalizes_default_notes_prompt():
    payload = transfer_services.build_transfer_payload(
        source_account_id=2,
        destination_account_id=3,
        amount="0.01",
        date_label="2026-08-04",
        time_label="07:30 PM",
        notes_label="Add notes",
    )

    assert payload["amount_centavos"] == 1
    assert payload["notes"] == ""


def test_save_transfer_returns_validation_failure_without_dependencies(
    monkeypatch,
):
    build_payload = Mock()
    get_account_by_id = Mock()
    insert_transfer = Mock()
    monkeypatch.setattr(
        transfer_services,
        "build_transfer_payload",
        build_payload,
    )
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

    result = transfer_services.save_transfer(
        **make_transfer_arguments(destination_account_id=2)
    )

    assert result == transfer_services.TransferSaveResult(
        False,
        "Source and destination accounts must be different.",
    )
    build_payload.assert_not_called()
    get_account_by_id.assert_not_called()
    insert_transfer.assert_not_called()


def test_save_transfer_rejects_invalid_date_before_database_access(
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

    result = transfer_services.save_transfer(
        **make_transfer_arguments(date_label="not a date")
    )

    assert result == transfer_services.TransferSaveResult(
        False,
        "Please select a valid date and time.",
    )
    get_account_by_id.assert_not_called()
    insert_transfer.assert_not_called()


@pytest.mark.parametrize(
    ("accounts", "message", "expected_calls"),
    [
        ([None], "Source account no longer exists.", [call(2)]),
        (
            [AccountRecord(2, "Cash"), None],
            "Destination account no longer exists.",
            [call(2), call(3)],
        ),
    ],
)
def test_save_transfer_rejects_missing_accounts(
    monkeypatch,
    accounts,
    message,
    expected_calls,
):
    get_account_by_id = Mock(side_effect=accounts)
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

    result = transfer_services.save_transfer(**make_transfer_arguments())

    assert result == transfer_services.TransferSaveResult(False, message)
    assert get_account_by_id.call_args_list == expected_calls
    insert_transfer.assert_not_called()


def test_save_transfer_handles_account_database_failure(monkeypatch):
    get_account_by_id = Mock(side_effect=sqlite3.OperationalError)
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

    result = transfer_services.save_transfer(**make_transfer_arguments())

    assert result == transfer_services.TransferSaveResult(
        False,
        "Accounts could not be verified.",
    )
    insert_transfer.assert_not_called()


@pytest.mark.parametrize(
    ("repository_result", "success", "message"),
    [
        (True, True, "Transfer added successfully."),
        (False, False, "Transfer could not be added."),
    ],
)
def test_save_transfer_returns_create_result(
    monkeypatch,
    repository_result,
    success,
    message,
):
    get_account_by_id = patch_valid_accounts(monkeypatch)
    insert_transfer = Mock(return_value=repository_result)
    update_transfer = Mock()
    monkeypatch.setattr(
        transfer_services,
        "insert_transfer",
        insert_transfer,
    )
    monkeypatch.setattr(
        transfer_services,
        "update_transfer",
        update_transfer,
    )

    result = transfer_services.save_transfer(**make_transfer_arguments())

    assert result == transfer_services.TransferSaveResult(success, message)
    assert get_account_by_id.call_args_list == [call(2), call(3)]
    insert_transfer.assert_called_once_with(
        2,
        3,
        12345,
        "2026-08-04 19:30:00",
        "Emergency fund",
        "internal",
        None,
    )
    update_transfer.assert_not_called()


def test_save_transfer_handles_create_database_failure(monkeypatch):
    patch_valid_accounts(monkeypatch)
    monkeypatch.setattr(
        transfer_services,
        "insert_transfer",
        Mock(side_effect=sqlite3.OperationalError),
    )

    result = transfer_services.save_transfer(**make_transfer_arguments())

    assert result == transfer_services.TransferSaveResult(
        False,
        "Transfer could not be added.",
    )


def test_transfer_service_workflow_preserves_one_centavo_and_restore():
    assert insert_account("Cash") is True
    assert insert_account("Savings") is True

    created = transfer_services.save_transfer(
        **make_transfer_arguments(
            source_account_id=1,
            destination_account_id=2,
            amount="0.01",
        )
    )

    assert created == transfer_services.TransferSaveResult(
        True,
        "Transfer added successfully.",
    )
    transfer = get_transfer_by_id(1)
    assert transfer.amount_centavos == 1

    deleted = transfer_services.delete_transfer_by_id(1)

    assert deleted.success is True
    assert deleted.deleted_transfer == transfer
    assert get_transfer_by_id(1) is None

    restored = transfer_services.restore_deleted_transfer(
        deleted.deleted_transfer
    )

    assert restored == transfer_services.TransferRestoreResult(
        True,
        "Transfer restored.",
    )
    assert get_transfer_by_id(1) == transfer


@pytest.mark.parametrize(
    ("repository_result", "success", "message"),
    [
        (True, True, "Transfer updated successfully."),
        (False, False, "Transfer could not be updated."),
    ],
)
def test_save_transfer_returns_update_result(
    monkeypatch,
    repository_result,
    success,
    message,
):
    patch_valid_accounts(monkeypatch)
    insert_transfer = Mock()
    update_transfer = Mock(return_value=repository_result)
    monkeypatch.setattr(
        transfer_services,
        "insert_transfer",
        insert_transfer,
    )
    monkeypatch.setattr(
        transfer_services,
        "update_transfer",
        update_transfer,
    )

    result = transfer_services.save_transfer(
        **make_transfer_arguments(transfer_id=17)
    )

    assert result == transfer_services.TransferSaveResult(success, message)
    insert_transfer.assert_not_called()
    update_transfer.assert_called_once_with(
        2,
        3,
        12345,
        "2026-08-04 19:30:00",
        "Emergency fund",
        17,
        "internal",
        None,
    )


def test_get_transfer_for_edit_forwards_transfer_id(monkeypatch):
    transfer = make_transfer()
    get_transfer_by_id = Mock(return_value=transfer)
    monkeypatch.setattr(
        transfer_services,
        "get_transfer_by_id",
        get_transfer_by_id,
    )

    assert transfer_services.get_transfer_for_edit(17) is transfer
    get_transfer_by_id.assert_called_once_with(17)


@pytest.mark.parametrize("repository_result", [True, False])
def test_delete_transfer_by_id_returns_repository_result(
    monkeypatch,
    repository_result,
):
    transfer = make_transfer()
    get_transfer_by_id = Mock(return_value=transfer)
    delete_transfer = Mock(return_value=repository_result)
    monkeypatch.setattr(
        transfer_services,
        "get_transfer_by_id",
        get_transfer_by_id,
    )
    monkeypatch.setattr(
        transfer_services,
        "delete_transfer",
        delete_transfer,
    )

    result = transfer_services.delete_transfer_by_id(17)

    assert result == transfer_services.TransferDeleteResult(
        success=repository_result,
        message=(
            "Transfer deleted."
            if repository_result
            else "Transfer could not be deleted."
        ),
        deleted_transfer=(transfer if repository_result else None),
    )
    get_transfer_by_id.assert_called_once_with(17)
    delete_transfer.assert_called_once_with(17)


def test_delete_missing_transfer_skips_repository_delete(monkeypatch):
    get_transfer_by_id = Mock(return_value=None)
    delete_transfer = Mock()
    monkeypatch.setattr(
        transfer_services,
        "get_transfer_by_id",
        get_transfer_by_id,
    )
    monkeypatch.setattr(
        transfer_services,
        "delete_transfer",
        delete_transfer,
    )

    result = transfer_services.delete_transfer_by_id(17)

    assert result == transfer_services.TransferDeleteResult(
        False,
        "Transfer could not be deleted.",
    )
    delete_transfer.assert_not_called()


@pytest.mark.parametrize("dependency_name", ["read", "delete"])
def test_delete_transfer_handles_database_failure(
    monkeypatch,
    dependency_name,
):
    get_transfer_by_id = Mock(return_value=make_transfer())
    delete_transfer = Mock(return_value=True)

    if dependency_name == "read":
        get_transfer_by_id.side_effect = sqlite3.OperationalError
    else:
        delete_transfer.side_effect = sqlite3.OperationalError

    monkeypatch.setattr(
        transfer_services,
        "get_transfer_by_id",
        get_transfer_by_id,
    )
    monkeypatch.setattr(
        transfer_services,
        "delete_transfer",
        delete_transfer,
    )

    assert transfer_services.delete_transfer_by_id(17) == (
        transfer_services.TransferDeleteResult(
            False,
            "Transfer could not be deleted.",
        )
    )


@pytest.mark.parametrize("repository_result", [True, False])
def test_restore_deleted_transfer_returns_repository_result(
    monkeypatch,
    repository_result,
):
    transfer = make_transfer()
    patch_valid_accounts(monkeypatch)
    restore_transfer = Mock(return_value=repository_result)
    monkeypatch.setattr(
        transfer_services,
        "restore_transfer",
        restore_transfer,
    )

    result = transfer_services.restore_deleted_transfer(transfer)

    assert result == transfer_services.TransferRestoreResult(
        success=repository_result,
        message=(
            "Transfer restored."
            if repository_result
            else "Transfer could not be restored."
        ),
    )
    restore_transfer.assert_called_once_with(transfer)


def test_restore_deleted_transfer_rejects_missing_account(monkeypatch):
    transfer = make_transfer()
    get_account_by_id = Mock(return_value=None)
    restore_transfer = Mock()
    monkeypatch.setattr(
        transfer_services,
        "get_account_by_id",
        get_account_by_id,
    )
    monkeypatch.setattr(
        transfer_services,
        "restore_transfer",
        restore_transfer,
    )

    result = transfer_services.restore_deleted_transfer(transfer)

    assert result == transfer_services.TransferRestoreResult(
        False,
        "Source account no longer exists.",
    )
    restore_transfer.assert_not_called()


def test_restore_deleted_transfer_handles_database_failure(monkeypatch):
    transfer = make_transfer()
    patch_valid_accounts(monkeypatch)
    restore_transfer = Mock(side_effect=sqlite3.OperationalError)
    monkeypatch.setattr(
        transfer_services,
        "restore_transfer",
        restore_transfer,
    )

    result = transfer_services.restore_deleted_transfer(transfer)

    assert result == transfer_services.TransferRestoreResult(
        False,
        "Transfer could not be restored.",
    )
