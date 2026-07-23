from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from screens.settings import SettingsScreen


@pytest.mark.parametrize(
    ("repository_result", "expected_message"),
    [
        (True, "All data has been deleted."),
        (False, "Data could not be deleted."),
    ],
)
def test_clear_data_renders_repository_result(
    monkeypatch,
    repository_result,
    expected_message,
):
    settings_module = import_module("screens.settings")
    clear_database = Mock(return_value=repository_result)
    show_snackbar = Mock()
    monkeypatch.setattr(
        settings_module,
        "clear_database",
        clear_database,
    )
    monkeypatch.setattr(
        settings_module,
        "show_snackbar",
        show_snackbar,
    )

    dashboard = SimpleNamespace(load_dashboard=Mock())
    manager = SimpleNamespace(
        current="settings",
        get_screen=Mock(return_value=dashboard),
    )
    screen = SimpleNamespace(
        close_clear_data_dialog=Mock(),
        manager=manager,
    )

    SettingsScreen.perform_clear_data(screen)

    clear_database.assert_called_once_with()
    screen.close_clear_data_dialog.assert_called_once_with()
    show_snackbar.assert_called_once_with(expected_message)

    if repository_result:
        manager.get_screen.assert_called_once_with("dashboard")
        dashboard.load_dashboard.assert_called_once_with()
        assert manager.current == "dashboard"
    else:
        manager.get_screen.assert_not_called()
        dashboard.load_dashboard.assert_not_called()
        assert manager.current == "settings"
        