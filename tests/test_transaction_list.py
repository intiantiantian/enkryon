from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock


def make_transaction(
    transaction_id,
    transaction_type="income",
    posting_status="posted",
):
    return SimpleNamespace(
        transaction_id=transaction_id,
        account_name="Cash",
        group_name="Salary",
        category_name="Monthly",
        amount_centavos=2500,
        transaction_type=transaction_type,
        posting_status=posting_status,
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
        "record_type",
        "screen",
        "account_name",
        "group_name",
        "category_name",
        "amount_text",
        "date_time_text",
        "transaction_type_icon",
        "transaction_type_label",
        "transaction_type_color",
        "posting_status",
        "transfer_kind",
        "counterparty",
        "is_temporary",
        "posting_status_label",
        "posting_status_color",
    }
    assert set(income_data) == expected_keys
    assert set(expense_data) == expected_keys
    assert income_data["transaction_type_label"] == "INCOME"
    assert income_data["record_type"] == "transaction"
    assert income_data["transaction_type_icon"] == "arrow-up"
    assert income_data["amount_text"] == "+ ₱ 25.00"
    assert expense_data["transaction_type_label"] == "EXPENSE"
    assert expense_data["transaction_type_icon"] == "arrow-down"
    assert expense_data["amount_text"] == "- ₱ 25.00"
    assert income_data["posting_status"] == "posted"
    assert income_data["is_temporary"] is False
    assert income_data["posting_status_label"] == ""


def test_temporary_transaction_card_has_visible_status_state():
    card_module = import_module("widgets.transaction_card")

    data = card_module.create_transaction_card_data(
        make_transaction(
            3,
            "expense",
            posting_status="temporary",
        ),
        object(),
    )

    assert data["posting_status"] == "temporary"
    assert data["is_temporary"] is True
    assert data["posting_status_label"] == "PENDING"
    assert "posting_status_icon" not in data


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
    screen.confirm_delete_transaction.assert_called_once_with(
        18,
        "posted",
    )


def test_temporary_card_exposes_post_action_for_current_record():
    card_module = import_module("widgets.transaction_card")
    screen = SimpleNamespace(confirm_post_transaction=Mock())
    card = SimpleNamespace(
        screen=screen,
        transaction_id=17,
        record_type="transaction",
        is_temporary=True,
    )

    card_module.TransactionCard.confirm_post_transaction(card)
    card.transaction_id = 18
    card_module.TransactionCard.confirm_post_transaction(card)

    assert screen.confirm_post_transaction.call_args_list == [
        ((17,), {}),
        ((18,), {}),
    ]


def test_posted_and_transfer_cards_ignore_post_action():
    card_module = import_module("widgets.transaction_card")
    screen = SimpleNamespace(confirm_post_transaction=Mock())

    posted = SimpleNamespace(
        screen=screen,
        transaction_id=17,
        record_type="transaction",
        is_temporary=False,
    )
    transfer = SimpleNamespace(
        screen=screen,
        transaction_id=18,
        record_type="transfer",
        is_temporary=True,
    )

    card_module.TransactionCard.confirm_post_transaction(posted)
    card_module.TransactionCard.confirm_post_transaction(transfer)

    screen.confirm_post_transaction.assert_not_called()


def test_transfer_card_shows_accounts_direction_and_neutral_amount():
    card_module = import_module("widgets.transaction_card")
    transfer = SimpleNamespace(
        record_id=7,
        record_type="transfer",
        transaction_id=7,
        activity_type="transfer",
        transaction_type="transfer",
        account_name="Cash",
        group_name="Account Transfer",
        category_name="Savings",
        source_account_name="Cash",
        destination_account_name="Savings",
        amount_centavos=10_025,
        direction="neutral",
        date_time="2026-08-04 19:30:00",
    )

    data = card_module.create_transaction_card_data(
        transfer,
        object(),
    )

    assert data["record_type"] == "transfer"
    assert data["transaction_id"] == 7
    assert data["account_name"] == "Cash to Savings"
    assert data["group_name"] == "Account Transfer"
    assert data["category_name"] == "Between accounts"
    assert data["amount_text"] == "₱ 100.25"
    assert data["transaction_type_label"] == "TRANSFER"
    assert data["transaction_type_icon"] == "swap-horizontal"
    assert data["posting_status"] == "posted"
    assert data["is_temporary"] is False


def test_transfer_card_uses_direction_aware_amount_and_actions():
    card_module = import_module("widgets.transaction_card")
    screen = SimpleNamespace(
        edit_transfer=Mock(),
        confirm_delete_transfer=Mock(),
    )
    card = SimpleNamespace(
        screen=screen,
        transaction_id=7,
        record_type="transfer",
    )

    card_module.TransactionCard.edit_transaction(card)
    card_module.TransactionCard.delete_transaction(card)

    screen.edit_transfer.assert_called_once_with(7)
    screen.confirm_delete_transfer.assert_called_once_with(7)


def test_transfer_card_formats_selected_account_direction():
    card_module = import_module("widgets.transaction_card")
    base = {
        "record_id": 7,
        "record_type": "transfer",
        "transaction_id": 7,
        "activity_type": "transfer",
        "transaction_type": "transfer",
        "account_name": "Cash",
        "group_name": "Account Transfer",
        "category_name": "Savings",
        "source_account_name": "Cash",
        "destination_account_name": "Savings",
        "amount_centavos": 10_025,
        "date_time": "2026-08-04 19:30:00",
    }

    incoming = card_module.create_transaction_card_data(
        SimpleNamespace(**base, direction="incoming"),
        object(),
    )
    outgoing = card_module.create_transaction_card_data(
        SimpleNamespace(**base, direction="outgoing"),
        object(),
    )

    assert incoming["amount_text"] == "+ ₱ 100.25"
    assert incoming["category_name"] == "Incoming transfer"
    assert outgoing["amount_text"] == "- ₱ 100.25"
    assert outgoing["category_name"] == "Outgoing transfer"


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


def test_pass_through_card_has_visible_kind_and_counterparty_text():
    card_module = import_module("widgets.transaction_card")
    transfer = SimpleNamespace(
        record_id=9,
        record_type="transfer",
        transaction_id=9,
        activity_type="transfer",
        transaction_type="transfer",
        account_name="Cash",
        group_name="Account Transfer",
        category_name="Bank",
        source_account_name="Cash",
        destination_account_name="Bank",
        amount_centavos=100_025,
        direction="neutral",
        date_time="2026-08-07 18:30:00",
        transfer_kind="pass_through",
        counterparty="Alex Rivera",
    )

    data = card_module.create_transaction_card_data(transfer, object())

    assert data["account_name"] == "Cash outflow | Bank inflow"
    assert data["group_name"] == "Pass-through Transfer"
    assert data["category_name"] == "Counterparty: Alex Rivera"
    assert data["transaction_type_label"] == "PASS-THROUGH"
    assert data["transfer_kind"] == "pass_through"
    assert data["counterparty"] == "Alex Rivera"
    assert data["amount_text"] == "₱ 1,000.25"


def test_recycled_card_data_clears_transfer_metadata_for_transactions():
    card_module = import_module("widgets.transaction_card")

    data = card_module.create_transaction_card_data(
        make_transaction(22, "expense"),
        object(),
    )

    assert data["transfer_kind"] == ""
    assert data["counterparty"] == ""
