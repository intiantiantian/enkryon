from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock


def make_transaction(transaction_id, transaction_type="income"):
    return SimpleNamespace(
        transaction_id=transaction_id,
        account_name="Cash",
        group_name="Salary",
        category_name="Monthly",
        amount_centavos=2500,
        transaction_type=transaction_type,
        date_time="2026-07-22 17:30:00",
    )


def test_transaction_empty_state_forwards_action(monkeypatch):
    card_module = import_module("widgets.transaction_card")
    empty_state_widget = object()
    empty_state_factory = Mock(return_value=empty_state_widget)
    monkeypatch.setattr(
        card_module,
        "EmptyState",
        empty_state_factory,
    )
    callback = Mock()
    state = {
        "title": "No transactions",
        "message": "Nothing matches this view.",
    }

    result = card_module.create_transaction_empty_state(
        state,
        action_text="SHOW ALL",
        action_callback=callback,
    )

    empty_state_factory.assert_called_once_with(
        icon="receipt-text-outline",
        title="No transactions",
        message="Nothing matches this view.",
        action_text="SHOW ALL",
        action_callback=callback,
    )
    assert result is empty_state_widget


def test_empty_transaction_list_renders_recovery_action(
    monkeypatch,
):
    list_module = import_module("widgets.transaction_list")
    empty_state_widget = object()
    empty_state_factory = Mock(return_value=empty_state_widget)
    monkeypatch.setattr(
        list_module,
        "create_transaction_empty_state",
        empty_state_factory,
    )
    container = SimpleNamespace(
        clear_widgets=Mock(),
        add_widget=Mock(),
    )
    callback = Mock()
    state = {
        "title": "No transactions",
        "message": "Nothing matches this view.",
    }

    list_module.render_transaction_list(
        container=container,
        transactions=[],
        screen=object(),
        empty_state=state,
        action_text="SHOW ALL",
        action_callback=callback,
    )

    container.clear_widgets.assert_called_once_with()
    empty_state_factory.assert_called_once_with(
        state,
        action_text="SHOW ALL",
        action_callback=callback,
    )
    container.add_widget.assert_called_once_with(
        empty_state_widget
    )


def test_virtualized_history_uses_data_for_ten_thousand_rows(
    monkeypatch,
):
    list_module = import_module("widgets.transaction_list")
    card_factory = Mock(
        side_effect=AssertionError(
            "History must not instantiate transaction cards."
        )
    )
    monkeypatch.setattr(
        list_module,
        "create_transaction_card",
        card_factory,
    )
    recycle_view = SimpleNamespace(data=[], scroll_y=0)
    empty_state_container = SimpleNamespace(
        clear_widgets=Mock(),
        add_widget=Mock(),
    )
    screen = object()
    transactions = [
        make_transaction(transaction_id)
        for transaction_id in range(1, 10_001)
    ]

    list_module.render_transaction_history(
        recycle_view=recycle_view,
        empty_state_container=empty_state_container,
        transactions=transactions,
        screen=screen,
        empty_state={},
    )

    assert len(recycle_view.data) == 10_000
    assert all(
        isinstance(row, dict)
        for row in recycle_view.data
    )
    assert recycle_view.data[0]["transaction_id"] == 1
    assert recycle_view.data[-1]["transaction_id"] == 10_000
    assert all(
        row["screen"] is screen
        for row in recycle_view.data
    )
    assert recycle_view.scroll_y == 1
    empty_state_container.clear_widgets.assert_called_once_with()
    empty_state_container.add_widget.assert_not_called()
    card_factory.assert_not_called()


def test_virtualized_history_tracks_all_recycled_card_state():
    card_module = import_module("widgets.transaction_card")
    screen = object()

    income_data = card_module.create_transaction_card_data(
        make_transaction(1, "income"),
        screen,
    )
    expense_data = card_module.create_transaction_card_data(
        make_transaction(2, "expense"),
        screen,
    )

    expected_keys = {
        "transaction_id",
        "screen",
        "account_name",
        "group_name",
        "category_name",
        "amount_text",
        "date_time_text",
        "transaction_type_icon",
        "transaction_type_label",
        "transaction_type_color",
    }
    assert set(income_data) == expected_keys
    assert set(expense_data) == expected_keys
    assert income_data["transaction_type_label"] == "INCOME"
    assert income_data["transaction_type_icon"] == "arrow-up"
    assert income_data["amount_text"] == "+ ₱ 25.00"
    assert expense_data["transaction_type_label"] == "EXPENSE"
    assert expense_data["transaction_type_icon"] == "arrow-down"
    assert expense_data["amount_text"] == "- ₱ 25.00"


def test_recycled_card_actions_use_refreshed_transaction_id():
    card_module = import_module("widgets.transaction_card")
    screen = SimpleNamespace(
        edit_transaction=Mock(),
        confirm_delete_transaction=Mock(),
    )
    card = SimpleNamespace(
        screen=screen,
        transaction_id=17,
    )

    card_module.TransactionCard.edit_transaction(card)
    card.transaction_id = 18
    card_module.TransactionCard.delete_transaction(card)

    screen.edit_transaction.assert_called_once_with(17)
    screen.confirm_delete_transaction.assert_called_once_with(18)


def test_empty_virtualized_history_renders_recovery_action(
    monkeypatch,
):
    list_module = import_module("widgets.transaction_list")
    empty_state_widget = object()
    empty_state_factory = Mock(return_value=empty_state_widget)
    monkeypatch.setattr(
        list_module,
        "create_transaction_empty_state",
        empty_state_factory,
    )
    recycle_view = SimpleNamespace(
        data=[{"transaction_id": 1}],
        scroll_y=0,
    )
    empty_state_container = SimpleNamespace(
        clear_widgets=Mock(),
        add_widget=Mock(),
    )
    callback = Mock()
    state = {
        "title": "No matching transactions",
        "message": "Try changing the filters.",
    }

    list_module.render_transaction_history(
        recycle_view=recycle_view,
        empty_state_container=empty_state_container,
        transactions=[],
        screen=object(),
        empty_state=state,
        action_text="SHOW ALL",
        action_callback=callback,
    )

    assert recycle_view.data == []
    assert recycle_view.scroll_y == 1
    empty_state_container.clear_widgets.assert_called_once_with()
    empty_state_factory.assert_called_once_with(
        state,
        action_text="SHOW ALL",
        action_callback=callback,
    )
    empty_state_container.add_widget.assert_called_once_with(
        empty_state_widget
    )
