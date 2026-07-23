from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, call

from theme.tokens import Colors, hex_to_rgba


def test_permanent_delete_confirmation_is_consistent(
    monkeypatch,
):
    confirmation_module = import_module(
        "widgets.delete_confirmation"
    )
    cancel_button = object()
    delete_button = object()
    button_factory = Mock(
        side_effect=[cancel_button, delete_button]
    )
    dialog = SimpleNamespace(open=Mock())
    dialog_factory = Mock(return_value=dialog)
    monkeypatch.setattr(
        confirmation_module,
        "MDFlatButton",
        button_factory,
    )
    monkeypatch.setattr(
        confirmation_module,
        "MDDialog",
        dialog_factory,
    )
    cancel_callback = Mock()
    delete_callback = Mock()

    result = (
        confirmation_module.open_permanent_delete_confirmation(
            title="Delete record?",
            message="This record is deleted permanently.",
            cancel_callback=cancel_callback,
            delete_callback=delete_callback,
        )
    )

    assert button_factory.call_args_list == [
        call(
            text="CANCEL",
            on_release=cancel_callback,
        ),
        call(
            text="DELETE",
            theme_text_color="Custom",
            text_color=hex_to_rgba(Colors.ERROR),
            on_release=delete_callback,
        ),
    ]
    dialog_factory.assert_called_once_with(
        title="Delete record?",
        text="This record is deleted permanently.",
        buttons=[cancel_button, delete_button],
    )
    dialog.open.assert_called_once_with()
    assert result is dialog
