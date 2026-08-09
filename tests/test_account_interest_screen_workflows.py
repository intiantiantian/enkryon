from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, patch

from screens.accounts import AccountsScreen
from services.interest_services import InterestProfileActionResult


accounts_module = import_module("screens.accounts")
action_results_module = import_module("screens.action_results")


def interest_state(enabled=True):
    return SimpleNamespace(
        enabled=enabled,
        configured=True,
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
        open_interest_reconciliation=Mock(),
        confirm_remove_interest=Mock(),
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
    assert kwargs["can_remove"] is True

    kwargs["save_callback"]("4.25", "2026-09-01")
    kwargs["disable_callback"]("2026-10-01")
    kwargs["reconcile_callback"]()
    kwargs["remove_callback"]()
    screen.save_interest_settings.assert_called_once_with(
        7, "4.25", "2026-09-01"
    )
    screen.disable_interest_settings.assert_called_once_with(
        7, "2026-10-01"
    )
    screen.open_interest_reconciliation.assert_called_once_with(
        7, "Savings"
    )
    screen.confirm_remove_interest.assert_called_once_with(7, "Savings")


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


def test_open_reconciliation_populates_preview_and_callbacks(monkeypatch):
    from services.interest_services import InterestReconciliationPreview

    dialog = SimpleNamespace(open=Mock())
    dialog_factory = Mock(return_value=dialog)
    preview = InterestReconciliationPreview(3, 425)
    monkeypatch.setattr(
        accounts_module,
        "InterestReconciliationDialog",
        dialog_factory,
    )
    monkeypatch.setattr(
        accounts_module,
        "get_interest_reconciliation_preview",
        Mock(return_value=preview),
    )
    screen = SimpleNamespace(
        reconcile_interest_credit=Mock(),
        open_interest_category_menu=Mock(),
        refresh_interest_reconciliation_preview=Mock(),
    )

    with patch("screens.accounts.date") as mocked_date:
        mocked_date.today.return_value.isoformat.return_value = "2026-08-09"
        AccountsScreen.open_interest_reconciliation(screen, 7, "Savings")

    dialog.open.assert_called_once_with()
    kwargs = dialog_factory.call_args.kwargs
    assert kwargs["account_name"] == "Savings"
    assert kwargs["estimated_text"] == "₱ 4.25"
    assert kwargs["accrual_count_text"] == "3 estimated days"
    assert kwargs["credit_date_text"] == "2026-08-09"
    kwargs["save_callback"]("4.21", "2026-08-09", 9)
    screen.reconcile_interest_credit.assert_called_once_with(
        7, "4.21", "2026-08-09", 9
    )


def test_reconcile_interest_credit_parses_amount_and_refreshes(monkeypatch):
    from services.interest_services import InterestReconciliationResult

    result = InterestReconciliationResult(
        True,
        "Posted.",
        posted_transaction_id=42,
        accrual_count=3,
        estimated_centavos=425,
        actual_centavos=421,
        variance_centavos=-4,
    )
    reconcile = Mock(return_value=result)
    show_snackbar = Mock()
    monkeypatch.setattr(accounts_module, "reconcile_interest_credit", reconcile)
    monkeypatch.setattr(action_results_module, "show_snackbar", show_snackbar)
    screen = SimpleNamespace(load_accounts=Mock())

    success = AccountsScreen.reconcile_interest_credit(
        screen,
        7,
        "4.21",
        "2026-08-09",
        9,
    )

    assert success is True
    reconcile.assert_called_once_with(
        account_id=7,
        actual_amount_centavos=421,
        credit_date="2026-08-09",
        category_id=9,
    )
    screen.load_accounts.assert_called_once_with()
    show_snackbar.assert_called_once_with("Posted.")


def test_confirm_remove_interest_explains_destructive_scope(monkeypatch):
    dialog = SimpleNamespace(open=Mock(), dismiss=Mock())
    dialog_factory = Mock(return_value=dialog)
    monkeypatch.setattr(
        accounts_module,
        "EnkryonConfirmationDialog",
        dialog_factory,
    )
    screen = SimpleNamespace(
        interest_remove_dialog=None,
        perform_remove_interest=Mock(),
        close_interest_remove_dialog=Mock(),
    )

    AccountsScreen.confirm_remove_interest(screen, 7, "Savings")

    dialog.open.assert_called_once_with()
    kwargs = dialog_factory.call_args.kwargs
    assert kwargs["title"] == "Remove Interest?"
    assert kwargs["confirm_text"] == "Remove"
    assert (
        "posted bank-interest Income transactions will remain"
        in kwargs["message"]
    )
    kwargs["confirm_callback"]()
    screen.perform_remove_interest.assert_called_once_with(7)


def test_perform_remove_interest_refreshes_account_cards(monkeypatch):
    from services.interest_services import InterestRemovalResult

    remove = Mock(
        return_value=InterestRemovalResult(
            True,
            "Removed.",
            removed_profiles=2,
            removed_accruals=4,
        )
    )
    show_snackbar = Mock()
    monkeypatch.setattr(accounts_module, "remove_interest_tracking", remove)
    monkeypatch.setattr(action_results_module, "show_snackbar", show_snackbar)
    screen = SimpleNamespace(
        interest_remove_dialog=None,
        load_accounts=Mock(),
        close_interest_remove_dialog=Mock(),
    )

    success = AccountsScreen.perform_remove_interest(screen, 7)

    assert success is True
    remove.assert_called_once_with(7)
    screen.load_accounts.assert_called_once_with()
    show_snackbar.assert_called_once_with("Removed.")
