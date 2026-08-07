from datetime import date

import pytest

from screens.transaction_filter_state import TransactionFilterState


def test_empty_filter_state_has_all_filter_defaults():
    state = TransactionFilterState()

    assert state == TransactionFilterState(
        search_text="",
        transaction_type=None,
        posting_status=None,
        transfer_kind=None,
        account_id=None,
        account_name="All Accounts",
        group_id=None,
        group_name="All Category Groups",
        category_id=None,
        category_name="All Categories",
        start_date=None,
        end_date=None,
    )
    assert state.is_active is False


def test_filter_state_normalizes_search_text():
    state = TransactionFilterState(search_text="  lunch  ")

    assert state.search_text == "lunch"
    assert state.to_query_arguments()["search_text"] == "lunch"

    state.set_search_text("   ")

    assert state.search_text == ""
    assert state.to_query_arguments()["search_text"] is None


def test_filter_state_selects_and_clears_account():
    state = TransactionFilterState()

    state.select_account(7, "Cash")

    assert state.account_id == 7
    assert state.account_name == "Cash"

    state.clear_account_selection()

    assert state.account_id is None
    assert state.account_name == "All Accounts"


def test_changing_transaction_type_clears_group_and_category():
    state = TransactionFilterState(
        transaction_type="income",
        group_id=3,
        group_name="Salary",
        category_id=5,
        category_name="Paycheck",
    )

    state.select_transaction_type("expense")

    assert state.transaction_type == "expense"
    assert state.group_id is None
    assert state.group_name == "All Category Groups"
    assert state.category_id is None
    assert state.category_name == "All Categories"


def test_reselecting_transaction_type_preserves_dependent_filters():
    state = TransactionFilterState(
        transaction_type="expense",
        group_id=3,
        group_name="Food",
        category_id=5,
        category_name="Lunch",
    )

    state.select_transaction_type("expense")

    assert state.group_id == 3
    assert state.category_id == 5


def test_selecting_group_sets_type_and_clears_previous_category():
    state = TransactionFilterState(
        transaction_type="income",
        group_id=3,
        group_name="Salary",
        category_id=5,
        category_name="Paycheck",
    )

    state.select_group(8, "Food", "expense")

    assert state.transaction_type == "expense"
    assert state.group_id == 8
    assert state.group_name == "Food"
    assert state.category_id is None
    assert state.category_name == "All Categories"


def test_selecting_category_sets_its_parent_filters():
    state = TransactionFilterState()

    state.select_category(
        9,
        "Lunch",
        8,
        "Food",
        "expense",
    )

    assert state.transaction_type == "expense"
    assert state.group_id == 8
    assert state.group_name == "Food"
    assert state.category_id == 9
    assert state.category_name == "Lunch"


def test_filter_state_accepts_same_day_date_range():
    selected_date = date(2026, 7, 20)
    state = TransactionFilterState()

    state.set_date_range(selected_date, selected_date)

    assert state.start_date == selected_date
    assert state.end_date == selected_date


def test_filter_state_rejects_reversed_date_range():
    state = TransactionFilterState()

    with pytest.raises(
        ValueError,
        match="Start date cannot be after end date.",
    ):
        state.set_date_range(
            date(2026, 7, 21),
            date(2026, 7, 20),
        )


def test_filter_state_builds_complete_query_arguments():
    state = TransactionFilterState(
        search_text=" lunch ",
        transaction_type="expense",
        account_id=7,
        account_name="Cash",
        group_id=8,
        group_name="Food",
        category_id=9,
        category_name="Lunch",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 20),
    )

    assert state.to_query_arguments() == {
        "search_text": "lunch",
        "account_id": 7,
        "activity_type": "expense",
        "posting_status": "posted",
        "transfer_kind": None,
        "group_id": 8,
        "category_id": 9,
        "start_date": date(2026, 7, 1),
        "end_date": date(2026, 7, 20),
    }
    assert state.is_active is True


def test_reset_restores_full_unfiltered_state():
    state = TransactionFilterState(
        search_text="lunch",
        transaction_type="expense",
        account_id=7,
        account_name="Cash",
        group_id=8,
        group_name="Food",
        category_id=9,
        category_name="Lunch",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 20),
    )

    state.reset()

    assert state == TransactionFilterState()
    assert state.to_query_arguments() == {
        "search_text": None,
        "account_id": None,
        "activity_type": None,
        "posting_status": None,
        "transfer_kind": None,
        "group_id": None,
        "category_id": None,
        "start_date": None,
        "end_date": None,
    }
    assert state.is_active is False


def test_pending_filter_sets_temporary_status_without_type():
    state = TransactionFilterState()

    state.select_activity_filter("pending")

    assert state.transaction_type is None
    assert state.posting_status == "temporary"
    assert state.active_filter_labels == ["Pending"]
    assert state.to_query_arguments()["posting_status"] == "temporary"


def test_income_and_expense_filters_are_explicitly_posted_only():
    state = TransactionFilterState()

    state.select_activity_filter("income")

    assert state.transaction_type == "income"
    assert state.posting_status == "posted"

    state.select_activity_filter("expense")

    assert state.transaction_type == "expense"
    assert state.posting_status == "posted"


def test_pending_category_filter_preserves_pending_scope():
    state = TransactionFilterState()
    state.select_activity_filter("pending")

    state.select_category(
        9,
        "Lunch",
        8,
        "Food",
        "expense",
    )

    assert state.transaction_type == "expense"
    assert state.posting_status == "temporary"
    assert state.active_filter_labels[:2] == ["Pending", "Expense"]


def test_switching_from_pending_to_posted_filter_clears_category_scope():
    state = TransactionFilterState(
        transaction_type="expense",
        posting_status="temporary",
        group_id=8,
        group_name="Food",
        category_id=9,
        category_name="Lunch",
    )

    state.select_activity_filter("expense")

    assert state.posting_status == "posted"
    assert state.group_id is None
    assert state.category_id is None


def test_transfer_kind_filter_selects_pass_through_scope():
    state = TransactionFilterState()

    state.select_transfer_kind("pass_through")

    assert state.transaction_type == "transfer"
    assert state.posting_status is None
    assert state.transfer_kind == "pass_through"
    assert state.active_filter_labels == ["Transfer: Pass-through"]
    assert state.to_query_arguments()["transfer_kind"] == "pass_through"


def test_general_transfer_filter_clears_transfer_kind_scope():
    state = TransactionFilterState(transfer_kind="internal")

    state.select_activity_filter("transfer")

    assert state.transaction_type == "transfer"
    assert state.transfer_kind is None
    assert state.active_filter_labels == ["Transfer"]


def test_transfer_kind_filter_rejects_unknown_kind():
    state = TransactionFilterState()

    with pytest.raises(ValueError, match="Unsupported transfer kind"):
        state.select_transfer_kind("external")


def test_transfer_kind_constructor_normalizes_to_transfer_activity():
    state = TransactionFilterState(
        transaction_type="expense",
        posting_status="temporary",
        transfer_kind="internal",
    )

    assert state.transaction_type == "transfer"
    assert state.posting_status is None
    assert state.transfer_kind == "internal"
