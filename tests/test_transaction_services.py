from unittest.mock import Mock

import pytest

from services import transaction_services


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


@pytest.mark.parametrize(
    "repository_result",
    [True, False],
)
def test_delete_transaction_by_id_returns_repository_result(
    monkeypatch,
    repository_result,
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

    assert result is repository_result
    repository_delete_transaction.assert_called_once_with(17)
