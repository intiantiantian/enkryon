from datetime import date

from unittest.mock import Mock

import pytest

from database.records import TransactionDetailRecord
from services import transaction_services


def make_transaction_payload():
    return {
        "account_id": 2,
        "amount_centavos": 12345,
        "category_id": 8,
        "date_time": "2026-07-19 19:30:00",
        "notes": "Dinner",
    }


def make_transaction(posting_status="posted"):
    return TransactionDetailRecord(
        transaction_id=17,
        account_id=2,
        amount_centavos=12345,
        category_id=8,
        date_time="2026-07-19 19:30:00",
        notes="Dinner",
        account_name="Cash",
        category_name="Dining",
        group_id=5,
        group_name="Food",
        transaction_type="expense",
        posting_status=posting_status,
    )


def test_save_transaction_returns_validation_failure(
    monkeypatch,
):
    validate_transaction_form = Mock(
        return_value=(
            False,
            "Please select an account.",
        )
    )
    build_transaction_payload = Mock()
    insert_transaction = Mock()
    update_transaction = Mock()

    monkeypatch.setattr(
        transaction_services,
        "validate_transaction_form",
        validate_transaction_form,
    )
    monkeypatch.setattr(
        transaction_services,
        "build_transaction_payload",
        build_transaction_payload,
    )
    monkeypatch.setattr(
        transaction_services,
        "insert_transaction",
        insert_transaction,
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction",
        update_transaction,
    )

    result = transaction_services.save_transaction(
        account_id=None,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
    )

    assert result == (
        transaction_services.TransactionSaveResult(
            success=False,
            message="Please select an account.",
        )
    )
    validate_transaction_form.assert_called_once_with(
        account_id=None,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
    )
    build_transaction_payload.assert_not_called()
    insert_transaction.assert_not_called()
    update_transaction.assert_not_called()


@pytest.mark.parametrize(
    ("repository_result", "expected_result"),
    [
        (
            True,
            transaction_services.TransactionSaveResult(
                success=True,
                message="Transaction added successfully.",
            ),
        ),
        (
            False,
            transaction_services.TransactionSaveResult(
                success=False,
                message="Transaction could not be added.",
            ),
        ),
    ],
)
def test_save_transaction_returns_create_result(
    monkeypatch,
    repository_result,
    expected_result,
):
    payload = make_transaction_payload()
    validate_transaction_form = Mock(return_value=(True, None))
    build_transaction_payload = Mock(return_value=payload)
    insert_transaction = Mock(return_value=repository_result)
    update_transaction = Mock()
    monkeypatch.setattr(
        transaction_services,
        "validate_transaction_form",
        validate_transaction_form,
    )
    monkeypatch.setattr(
        transaction_services,
        "build_transaction_payload",
        build_transaction_payload,
    )
    monkeypatch.setattr(
        transaction_services,
        "insert_transaction",
        insert_transaction,
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction",
        update_transaction,
    )

    result = transaction_services.save_transaction(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
    )

    assert result == expected_result
    build_transaction_payload.assert_called_once_with(
        account_id=2,
        amount="123.45",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
    )
    insert_transaction.assert_called_once_with(
        2,
        12345,
        8,
        "2026-07-19 19:30:00",
        "Dinner",
        posting_status="posted",
    )
    update_transaction.assert_not_called()


@pytest.mark.parametrize(
    ("repository_result", "expected_result"),
    [
        (
            True,
            transaction_services.TransactionSaveResult(
                success=True,
                message=(
                    "Transaction updated successfully."
                ),
            ),
        ),
        (
            False,
            transaction_services.TransactionSaveResult(
                success=False,
                message=(
                    "Transaction could not be updated."
                ),
            ),
        ),
    ],
)
def test_save_transaction_returns_update_result(
    monkeypatch,
    repository_result,
    expected_result,
):
    payload = make_transaction_payload()

    monkeypatch.setattr(
        transaction_services,
        "validate_transaction_form",
        Mock(return_value=(True, None)),
    )
    monkeypatch.setattr(
        transaction_services,
        "build_transaction_payload",
        Mock(return_value=payload),
    )

    insert_transaction = Mock()
    get_transaction_by_id = Mock(return_value=make_transaction())
    update_transaction = Mock(
        return_value=repository_result
    )

    monkeypatch.setattr(
        transaction_services,
        "insert_transaction",
        insert_transaction,
    )
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        get_transaction_by_id,
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction",
        update_transaction,
    )

    result = transaction_services.save_transaction(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
        transaction_id=17,
    )

    assert result == expected_result
    insert_transaction.assert_not_called()
    get_transaction_by_id.assert_called_once_with(17)
    update_transaction.assert_called_once_with(
        2,
        12345,
        8,
        "2026-07-19 19:30:00",
        "Dinner",
        17,
    )


@pytest.mark.parametrize(
    (
        "transaction_filter",
        "compact",
        "account_filtered",
        "expected_state",
    ),
    [
        (
            "income",
            False,
            False,
            {
                "title": "No income transactions",
                "message": (
                    "No income transactions match the current view."
                ),
            },
        ),
        (
            "expense",
            False,
            False,
            {
                "title": "No expense transactions",
                "message": (
                    "No expense transactions match the current view."
                ),
            },
        ),
        (
            None,
            True,
            True,
            {
                "title": "No transactions for this account",
                "message": (
                    "This account does not have any transactions yet."
                ),
            },
        ),
        (
            None,
            True,
            False,
            {
                "title": "No transactions yet",
                "message": (
                    "Add a transaction to start tracking your money."
                ),
            },
        ),
        (
            None,
            False,
            False,
            {
                "title": "No transactions yet",
                "message": (
                    "Add a transaction to start building your history."
                ),
            },
        ),
    ],
)
def test_get_empty_transaction_state(
    transaction_filter,
    compact,
    account_filtered,
    expected_state,
):
    assert transaction_services.get_empty_transaction_state(
        transaction_filter,
        compact,
        account_filtered,
    ) == expected_state


def test_get_empty_transaction_state_reports_unmatched_advanced_filters():
    assert transaction_services.get_empty_transaction_state(
        transaction_type="expense",
        compact=True,
        account_filtered=True,
        advanced_filters_active=True,
    ) == {
        "title": "No matching transactions",
        "message": (
            "Try changing or resetting your search and filters."
        ),
    }


def test_get_transactions_for_view_forwards_filters(monkeypatch):
    expected_transactions = [(7, "Cash", "Salary")]
    start_date = date(2026, 7, 1)
    end_date = date(2026, 7, 20)
    repository_get_transactions = Mock(
        return_value=expected_transactions
    )
    monkeypatch.setattr(
        transaction_services,
        "get_transactions",
        repository_get_transactions,
    )

    result = transaction_services.get_transactions_for_view(
        account_id=3,
        transaction_type="expense",
        search_text="lunch",
        group_id=4,
        category_id=8,
        start_date=start_date,
        end_date=end_date,
        limit=5,
    )

    assert result == expected_transactions
    repository_get_transactions.assert_called_once_with(
        account_id=3,
        transaction_type="expense",
        search_text="lunch",
        group_id=4,
        category_id=8,
        start_date=start_date,
        end_date=end_date,
        limit=5,
    )


def test_get_transaction_list_data_combines_service_results(
    monkeypatch,
):
    expected_transactions = [(7, "Cash", "Salary")]
    start_date = date(2026, 7, 1)
    end_date = date(2026, 7, 20)
    expected_empty_state = {
        "title": "No matching transactions",
        "message": (
            "Try changing or resetting your search and filters."
        ),
    }
    get_transactions_for_view = Mock(
        return_value=expected_transactions
    )
    get_empty_transaction_state = Mock(
        return_value=expected_empty_state
    )

    monkeypatch.setattr(
        transaction_services,
        "get_transactions_for_view",
        get_transactions_for_view,
    )
    monkeypatch.setattr(
        transaction_services,
        "get_empty_transaction_state",
        get_empty_transaction_state,
    )

    result = transaction_services.get_transaction_list_data(
        account_id=2,
        transaction_type="income",
        search_text="salary",
        group_id=3,
        category_id=7,
        start_date=start_date,
        end_date=end_date,
        limit=10,
        compact_empty_state=True,
    )

    assert result == {
        "transactions": expected_transactions,
        "empty_state": expected_empty_state,
    }
    get_transactions_for_view.assert_called_once_with(
        account_id=2,
        transaction_type="income",
        search_text="salary",
        group_id=3,
        category_id=7,
        start_date=start_date,
        end_date=end_date,
        limit=10,
    )
    get_empty_transaction_state.assert_called_once_with(
        "income",
        True,
        account_filtered=True,
        advanced_filters_active=True,
    )


def test_get_transactions_for_view_propagates_repository_error(
    monkeypatch,
):
    repository_get_transactions = Mock(
        side_effect=RuntimeError("database unavailable")
    )
    monkeypatch.setattr(
        transaction_services,
        "get_transactions",
        repository_get_transactions,
    )

    with pytest.raises(RuntimeError, match="database unavailable"):
        transaction_services.get_transactions_for_view(
            account_id=3,
            transaction_type="expense",
            limit=5,
        )

    repository_get_transactions.assert_called_once_with(
        account_id=3,
        transaction_type="expense",
        search_text=None,
        group_id=None,
        category_id=None,
        start_date=None,
        end_date=None,
        limit=5,
    )


def test_get_transaction_for_edit_forwards_transaction_id(
    monkeypatch,
):
    expected_transaction = object()
    repository_get_transaction = Mock(
        return_value=expected_transaction
    )

    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        repository_get_transaction,
    )

    result = transaction_services.get_transaction_for_edit(17)

    assert result is expected_transaction
    repository_get_transaction.assert_called_once_with(17)


@pytest.mark.parametrize(
        "repository_result",
        [True, False],)
def test_delete_transaction_by_id_returns_repository_result(
    monkeypatch,
    repository_result,
):
    transaction = object()
    repository_get_transaction = Mock(
        return_value=transaction
    )
    repository_delete_transaction = Mock(
        return_value=repository_result
    )
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        repository_get_transaction,
    )
    monkeypatch.setattr(
        transaction_services,
        "delete_transaction",
        repository_delete_transaction,
    )

    result = transaction_services.delete_transaction_by_id(17)

    assert result == transaction_services.TransactionDeleteResult(
        success=repository_result,
        message=(
            "Transaction deleted."
            if repository_result
            else "Transaction could not be deleted."
        ),
        deleted_transaction=(
            transaction if repository_result else None
        ),
    )
    repository_get_transaction.assert_called_once_with(17)
    repository_delete_transaction.assert_called_once_with(17)


def test_delete_missing_transaction_skips_repository_delete(
    monkeypatch,
):
    repository_get_transaction = Mock(return_value=None)
    repository_delete_transaction = Mock()
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        repository_get_transaction,
    )
    monkeypatch.setattr(
        transaction_services,
        "delete_transaction",
        repository_delete_transaction,
    )

    result = transaction_services.delete_transaction_by_id(17)

    assert result == transaction_services.TransactionDeleteResult(
        success=False,
        message="Transaction could not be deleted.",
    )
    repository_get_transaction.assert_called_once_with(17)
    repository_delete_transaction.assert_not_called()


@pytest.mark.parametrize("restored",
                         [True, False],)
def test_restore_deleted_transaction_returns_repository_result(
    monkeypatch,
    restored,
):
    transaction = object()
    repository_restore_transaction = Mock(
        return_value=restored
    )
    monkeypatch.setattr(
        transaction_services,
        "restore_transaction",
        repository_restore_transaction,
    )

    result = transaction_services.restore_deleted_transaction(
        transaction
    )

    assert result == transaction_services.TransactionRestoreResult(
        success=restored,
        message=(
            "Transaction restored."
            if restored
            else "Transaction could not be restored."
        ),
    )
    repository_restore_transaction.assert_called_once_with(
        transaction
    )
