from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

from screens.accounts import AccountsScreen
from services.interest_services import InterestProfileActionResult


accounts_module = import_module("screens.accounts")
action_results_module = import_module("screens.action_results")


def interest_state(enabled=True):
    return SimpleNamespace(
        enabled=enabled,
        apr_text="3.65" if enabled else "",
        effective_date_text="2026-08-09",
        day_count_text="Actual/365",
        today_estimate_text="₱ 1.00",
        accumulated_estimate_text="₱ 5.00",
        summary_text="Interest: 3.65% APR · accrued ₱ 5.00",
    )


def test_open_interest_dialog_populates_account_state(monkeypatch):
    dialog = SimpleNamespace(open=Mock())
    dialog_factory = Mock(return_value=dialog)
    load_state = Mock(return_value=interest_state())
    monkeypatch.setattr(accounts_module, "InterestSettingsDialog", dialog_factory)
    monkeypatch.setattr(accounts_module, "load_account_interest_view", load_state)
    screen = SimpleNamespace(
        save_interest_settings=Mock(),
        disable_interest_settings=Mock(),
    )

    AccountsScreen.open_interest_dialog(screen, 7, "Savings")

    load_state.assert_called_once_with(7)
    dialog.open.assert_called_once_with()
    kwargs = dialog_factory.call_args.kwargs
    assert kwargs["account_name"] == "Savings"
    assert kwargs["apr_text"] == "3.65"
    assert kwargs["day_count_text"] == "Actual/365"
    assert kwargs["today_estimate_text"] == "₱ 1.00"
    assert kwargs["accumulated_estimate_text"] == "₱ 5.00"
    assert kwargs["is_enabled"] is True

    kwargs["save_callback"]("4.25", "2026-09-01")
    kwargs["disable_callback"]("2026-10-01")
    screen.save_interest_settings.assert_called_once_with(
        7, "4.25", "2026-09-01"
    )
    screen.disable_interest_settings.assert_called_once_with(
        7, "2026-10-01"
    )


def test_save_interest_settings_parses_and_refreshes(monkeypatch):
    save_profile = Mock(
        return_value=InterestProfileActionResult(True, "Saved.")
    )
    show_snackbar = Mock()
    monkeypatch.setattr(accounts_module, "save_interest_profile", save_profile)
    monkeypatch.setattr(action_results_module, "show_snackbar", show_snackbar)
    screen = SimpleNamespace(load_accounts=Mock())

    result = AccountsScreen.save_interest_settings(
        screen,
        7,
        "3.65",
        "2026-08-09",
    )

    assert result is True
    save_profile.assert_called_once_with(
        7,
        3_650_000,
        "2026-08-09",
        enabled=True,
    )
    screen.load_accounts.assert_called_once_with()
    show_snackbar.assert_called_once_with("Saved.")


def test_disable_interest_settings_inserts_effective_disabled_profile(monkeypatch):
    save_profile = Mock(
        return_value=InterestProfileActionResult(True, "Disabled.")
    )
    show_snackbar = Mock()
    monkeypatch.setattr(accounts_module, "save_interest_profile", save_profile)
    monkeypatch.setattr(action_results_module, "show_snackbar", show_snackbar)
    screen = SimpleNamespace(load_accounts=Mock())

    result = AccountsScreen.disable_interest_settings(
        screen,
        7,
        "2026-08-10",
    )

    assert result is True
    save_profile.assert_called_once_with(
        7,
        0,
        "2026-08-10",
        enabled=False,
    )
    screen.load_accounts.assert_called_once_with()
    show_snackbar.assert_called_once_with("Disabled.")


def test_invalid_apr_keeps_dialog_open_and_does_not_persist(monkeypatch):
    save_profile = Mock()
    snackbar_module = import_module("utils.snackbar")
    show_snackbar = Mock()
    monkeypatch.setattr(accounts_module, "save_interest_profile", save_profile)
    monkeypatch.setattr(snackbar_module, "show_snackbar", show_snackbar)
    screen = SimpleNamespace(load_accounts=Mock())

    result = AccountsScreen.save_interest_settings(
        screen,
        7,
        "1.0000001",
        "2026-08-09",
    )

    assert result is False
    save_profile.assert_not_called()
    screen.load_accounts.assert_not_called()
    show_snackbar.assert_called_once_with(
        "APR can use at most six decimal places."
    )
