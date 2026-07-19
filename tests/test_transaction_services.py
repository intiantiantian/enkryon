from unittest.mock import Mock

import pytest

from services import transaction_services


def make_transaction_payload():
    return {
        "account_id": 2,
        "amount_centavos": 12345,
        "category_id": 8,
        "date_time": "2026-07-19 19:30:00",
        "notes": "Dinner",
    }


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


def test_save_transaction_creates_valid_transaction(
    monkeypatch,
):
    payload = make_transaction_payload()
    validate_transaction_form = Mock(
        return_value=(True, None)
    )
    build_transaction_payload = Mock(
        return_value=payload
    )
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
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
    )

    assert result == (
        transaction_services.TransactionSaveResult(
            success=True,
            message="Transaction added successfully.",
        )
    )
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
        "expected_state",
    ),
    [
        (
            "income",
            False,
            {
                "title": "No income transactions found",
                "message": "Income transactions will appear here.",
            },
        ),
        (
            "expense",
            False,
            {
                "title": "No expense transactions found",
                "message": "Expense transactions will appear here.",
            },
        ),
        (
            None,
            True,
            {
                "title": "No transactions yet",
                "message": (
                    "Tap + Add Transaction to create your first "
                    "transaction."
                ),
            },
        ),
        (
            None,
            False,
            {
                "title": "No transactions yet",
                "message": (
                    "Go back to Dashboard and tap + Add Transaction."
                ),
            },
        ),
    ],
)
def test_get_empty_transaction_state(
    transaction_filter,
    compact,
    expected_state,
):
    assert transaction_services.get_empty_transaction_state(
        transaction_filter,
        compact,
    ) == expected_state


def test_get_transactions_for_view_forwards_filters(monkeypatch):
    expected_transactions = [(7, "Cash", "Salary")]
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
        transaction_filter="expense",
        limit=5,
    )

    assert result == expected_transactions
    repository_get_transactions.assert_called_once_with(
        account_id=3,
        transaction_type="expense",
        limit=5,
    )


def test_get_transaction_list_data_combines_service_results(
    monkeypatch,
):
    expected_transactions = [(7, "Cash", "Salary")]
    expected_empty_state = {
        "title": "No income transactions found",
        "message": "Income transactions will appear here.",
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
        transaction_filter="income",
        limit=10,
        compact_empty_state=True,
    )

    assert result == {
        "transactions": expected_transactions,
        "empty_state": expected_empty_state,
    }
    get_transactions_for_view.assert_called_once_with(
        account_id=2,
        transaction_filter="income",
        limit=10,
    )
    get_empty_transaction_state.assert_called_once_with(
        "income",
        True,
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
            transaction_filter="expense",
            limit=5,
        )

    repository_get_transactions.assert_called_once_with(
        account_id=3,
        transaction_type="expense",
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
    ("repository_result", "expected_result"),
    [
        (
            True,
            transaction_services.TransactionDeleteResult(
                success=True,
                message="Transaction deleted successfully.",
            ),
        ),
        (
            False,
            transaction_services.TransactionDeleteResult(
                success=False,
                message="Transaction could not be deleted.",
            ),
        ),
    ],
)
def test_delete_transaction_by_id_returns_repository_result(
    monkeypatch,
    repository_result,
    expected_result,
):
    repository_delete_transaction = Mock(
        return_value=repository_result
    )

    monkeypatch.setattr(
        transaction_services,
        "delete_transaction",
        repository_delete_transaction,
    )

    result = transaction_services.delete_transaction_by_id(17)

    assert result == expected_result
    repository_delete_transaction.assert_called_once_with(17)
