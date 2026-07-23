from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, patch


def test_application_module_imports_ui_dependencies():
    application = import_module("main")

    imported_screen_names = {
        application.DashboardScreen.__name__,
        application.AddTransactionScreen.__name__,
        application.SettingsScreen.__name__,
        application.AccountsScreen.__name__,
        application.CategoriesScreen.__name__,
        application.TransactionsScreen.__name__,
    }

    assert imported_screen_names == {
        "DashboardScreen",
        "AddTransactionScreen",
        "SettingsScreen",
        "AccountsScreen",
        "CategoriesScreen",
        "TransactionsScreen",
    }
    assert callable(application.EnkryonApp.build)


def test_back_button_dismisses_overlay_before_navigation():
    application = import_module("main")
    navigate = Mock()
    app = SimpleNamespace(
        BACK_KEY=application.EnkryonApp.BACK_KEY,
        root=SimpleNamespace(
            current="settings",
            current_screen=SimpleNamespace(
                go_to_dashboard=navigate,
            ),
        ),
    )

    with patch.object(
        application.EnkryonOverlay,
        "dismiss_active",
        return_value=True,
    ) as dismiss_active:
        handled = application.EnkryonApp.handle_back_button(
            app,
            application.Window,
            application.EnkryonApp.BACK_KEY,
        )

    assert handled is True
    dismiss_active.assert_called_once_with(application.Window)
    navigate.assert_not_called()


def test_back_button_navigates_when_no_overlay_is_active():
    application = import_module("main")
    navigate = Mock()
    app = SimpleNamespace(
        BACK_KEY=application.EnkryonApp.BACK_KEY,
        root=SimpleNamespace(
            current="settings",
            current_screen=SimpleNamespace(
                go_to_dashboard=navigate,
            ),
        ),
    )

    with patch.object(
        application.EnkryonOverlay,
        "dismiss_active",
        return_value=False,
    ) as dismiss_active:
        handled = application.EnkryonApp.handle_back_button(
            app,
            application.Window,
            application.EnkryonApp.BACK_KEY,
        )

    assert handled is True
    dismiss_active.assert_called_once_with(application.Window)
    navigate.assert_called_once_with()
