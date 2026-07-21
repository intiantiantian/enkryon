from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from main import EnkryonApp


@pytest.mark.parametrize(
    ("screen_name", "expected_method"),
    [
        ("accounts", "go_back"),
        ("categories", "go_back"),
        ("add_transaction", "go_to_dashboard"),
        ("transactions", "go_to_dashboard"),
        ("settings", "go_to_dashboard"),
    ],
)
def test_android_back_navigates_within_app(
    screen_name,
    expected_method,
):
    current_screen = SimpleNamespace(
        go_back=Mock(),
        go_to_dashboard=Mock(),
    )
    app = SimpleNamespace(
        BACK_KEY=27,
        root=SimpleNamespace(
            current=screen_name,
            current_screen=current_screen,
        ),
    )

    handled = EnkryonApp.handle_back_button(
        app,
        None,
        27,
    )

    assert handled is True
    getattr(
        current_screen,
        expected_method,
    ).assert_called_once_with()

    unused_method = (
        "go_to_dashboard"
        if expected_method == "go_back"
        else "go_back"
    )
    getattr(
        current_screen,
        unused_method,
    ).assert_not_called()


def test_android_back_allows_exit_from_dashboard():
    current_screen = SimpleNamespace(
        go_back=Mock(),
        go_to_dashboard=Mock(),
    )
    app = SimpleNamespace(
        BACK_KEY=27,
        root=SimpleNamespace(
            current="dashboard",
            current_screen=current_screen,
        ),
    )

    handled = EnkryonApp.handle_back_button(
        app,
        None,
        27,
    )

    assert handled is False
    current_screen.go_back.assert_not_called()
    current_screen.go_to_dashboard.assert_not_called()


def test_non_back_key_is_not_handled():
    current_screen = SimpleNamespace(
        go_back=Mock(),
        go_to_dashboard=Mock(),
    )
    app = SimpleNamespace(
        BACK_KEY=27,
        root=SimpleNamespace(
            current="accounts",
            current_screen=current_screen,
        ),
    )

    handled = EnkryonApp.handle_back_button(
        app,
        None,
        13,
    )

    assert handled is False
    current_screen.go_back.assert_not_called()
    current_screen.go_to_dashboard.assert_not_called()


def test_app_registers_and_unregisters_back_handler(
    monkeypatch,
):
    application = import_module("main")
    bind = Mock()
    unbind = Mock()
    handler = Mock()

    monkeypatch.setattr(
        application,
        "Window",
        SimpleNamespace(
            bind=bind,
            unbind=unbind,
        ),
    )

    app = SimpleNamespace(handle_back_button=handler)

    EnkryonApp.on_start(app)
    EnkryonApp.on_stop(app)

    bind.assert_called_once_with(
        on_key_down=handler,
    )
    unbind.assert_called_once_with(
        on_key_down=handler,
    )
