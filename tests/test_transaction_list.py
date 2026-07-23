from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock


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
