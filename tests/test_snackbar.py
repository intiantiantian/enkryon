from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock
from pathlib import Path

from widgets.snackbar import AppSnackbar


def test_show_snackbar_forwards_action_options(monkeypatch):
    snackbar_module = import_module("utils.snackbar")
    snackbar = SimpleNamespace(show=Mock())
    snackbar_factory = Mock(return_value=snackbar)
    monkeypatch.setattr(
        snackbar_module,
        "AppSnackbar",
        snackbar_factory,
    )
    callback = Mock()

    result = snackbar_module.show_snackbar(
        "Transaction deleted.",
        action_text="UNDO",
        action_callback=callback,
        duration=8,
    )

    snackbar_factory.assert_called_once_with()
    snackbar.show.assert_called_once_with(
        "Transaction deleted.",
        action_text="UNDO",
        action_callback=callback,
        duration=8,
    )
    assert result is snackbar


def test_snackbar_action_runs_once_and_cancels_timeout():
    callback = Mock()
    hide_event = SimpleNamespace(cancel=Mock())
    action_button = SimpleNamespace(disabled=False)
    snackbar = SimpleNamespace(
        _action_callback=callback,
        _hide_event=hide_event,
        ids=SimpleNamespace(action_button=action_button),
        hide=Mock(),
    )

    AppSnackbar.perform_action(snackbar)
    AppSnackbar.perform_action(snackbar)

    hide_event.cancel.assert_called_once_with()
    snackbar.hide.assert_called_once_with()
    callback.assert_called_once_with()
    assert snackbar._action_callback is None
    assert snackbar._hide_event is None
    assert action_button.disabled is True


def test_snackbar_action_button_is_vertically_centered():
    widgets_kv = Path("kv/widgets.kv").read_text(
        encoding="utf-8"
    )
    snackbar_rule = widgets_kv.split(
        "<AppSnackbar>:",
        1,
    )[1].split("<TransactionCard", 1)[0]
    action_button_rule = snackbar_rule.split(
        "MDFlatButton:",
        1,
    )[1]

    assert 'pos_hint: {"center_y": .5}' in action_button_rule
