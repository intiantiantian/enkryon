from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from screens.accounts import AccountsScreen
from services.account_services import AccountActionResult


action_results_module = import_module("screens.action_results")


def patch_account_action(
    monkeypatch,
    action_name,
    result,
):
    accounts_module = import_module("screens.accounts")
    action = Mock(return_value=result)
    show_snackbar = Mock()
    monkeypatch.setattr(accounts_module, action_name, action)
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    return action, show_snackbar


def test_load_accounts_renders_empty_state(monkeypatch):
    accounts_module = import_module("screens.accounts")
    get_accounts_for_view = Mock(return_value=[])
    empty_state = object()
    empty_state_factory = Mock(return_value=empty_state)
    monkeypatch.setattr(
        accounts_module,
        "get_accounts_for_view",
        get_accounts_for_view,
    )
    monkeypatch.setattr(
        accounts_module,
        "EmptyState",
        empty_state_factory,
    )
    container = SimpleNamespace(
        clear_widgets=Mock(),
        add_widget=Mock(),
    )
    screen = SimpleNamespace(
        ids=SimpleNamespace(accounts_container=container),
        add_account=Mock()
    )

    AccountsScreen.load_accounts(screen)

    get_accounts_for_view.assert_called_once_with()
    container.clear_widgets.assert_called_once_with()
    empty_state_factory.assert_called_once_with(
        icon="wallet-outline",
        title="No accounts yet",
        message="Create an account to start tracking your money.",
        action_text="ADD ACCOUNT",
        action_callback=screen.add_account,
    )
    container.add_widget.assert_called_once_with(empty_state)


def test_load_accounts_renders_account_cards(monkeypatch):
    accounts_module = import_module("screens.accounts")
    accounts = [
        SimpleNamespace(account_id=1, name="Cash"),
        SimpleNamespace(account_id=2, name="Savings"),
    ]
    get_accounts_for_view = Mock(return_value=accounts)
    cards = [
        SimpleNamespace(screen=None, set_account=Mock()),
        SimpleNamespace(screen=None, set_account=Mock()),
    ]
    account_card_factory = Mock(side_effect=cards)
    interest_states = [
        SimpleNamespace(summary_text="Interest: Off"),
        SimpleNamespace(summary_text="Interest: 3.65% APR · accrued ₱ 1.00"),
    ]
    load_interest = Mock(side_effect=interest_states)
    for card in cards:
        card.set_interest_summary = Mock()
    monkeypatch.setattr(
        accounts_module,
        "get_accounts_for_view",
        get_accounts_for_view,
    )
    monkeypatch.setattr(
        accounts_module,
        "load_account_interest_view",
        load_interest,
    )
    monkeypatch.setattr(
        accounts_module,
        "AccountCard",
        account_card_factory,
    )
    container = SimpleNamespace(
        clear_widgets=Mock(),
        add_widget=Mock(),
    )
    screen = SimpleNamespace(
        ids=SimpleNamespace(accounts_container=container),
    )

    AccountsScreen.load_accounts(screen)

    get_accounts_for_view.assert_called_once_with()
    container.clear_widgets.assert_called_once_with()
    assert account_card_factory.call_count == 2
    for card, account, interest_state in zip(cards, accounts, interest_states):
        assert card.screen is screen
        card.set_account.assert_called_once_with(account)
        card.set_interest_summary.assert_called_once_with(
            interest_state.summary_text
        )
    assert load_interest.call_args_list == [call(1), call(2)]
    assert container.add_widget.call_args_list == [
        call(cards[0]),
        call(cards[1]),
    ]


@pytest.mark.parametrize("success", [True, False])
def test_save_account_renders_service_result(
    monkeypatch,
    success,
):
    result = AccountActionResult(
        success,
        "Account action result.",
    )
    create_account_workflow, show_snackbar = patch_account_action(
        monkeypatch,
        "create_account_workflow",
        result,
    )
    account_created_callback = Mock()
    screen = SimpleNamespace(
        load_accounts=Mock(),
        account_created_callback=account_created_callback,
    )

    AccountsScreen.save_account(screen, " Cash ")

    create_account_workflow.assert_called_once_with(" Cash ")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_accounts.call_count == int(success)
    assert account_created_callback.call_args_list == (
        [call("Cash")] if success else []
    )


def test_open_rename_dialog_uses_custom_input_overlay(
    monkeypatch,
):
    accounts_module = import_module("screens.accounts")
    dialog = SimpleNamespace(open=Mock())
    dialog_factory = Mock(return_value=dialog)
    monkeypatch.setattr(
        accounts_module,
        "InputDialog",
        dialog_factory,
    )
    screen = SimpleNamespace(
        rename_account=Mock(),
    )

    AccountsScreen.open_rename_dialog(
        screen,
        7,
        "Cash",
    )

    dialog.open.assert_called_once_with()

    dialog_kwargs = dialog_factory.call_args.kwargs

    assert dialog_kwargs["title"] == "Rename Account"
    assert dialog_kwargs["hint_text"] == "Account name..."
    assert dialog_kwargs["text"] == "Cash"

    dialog_kwargs["callback"]("Wallet")

    screen.rename_account.assert_called_once_with(
        7,
        "Wallet",
    )


@pytest.mark.parametrize("success", [True, False])
def test_rename_account_renders_service_result(
    monkeypatch,
    success,
):
    result = AccountActionResult(
        success,
        "Account rename result.",
    )
    rename_account_workflow, show_snackbar = patch_account_action(
        monkeypatch,
        "rename_account_workflow",
        result,
    )
    screen = SimpleNamespace(
        load_accounts=Mock(),
    )

    AccountsScreen.rename_account(
        screen,
        7,
        " Wallet ",
    )

    rename_account_workflow.assert_called_once_with(7, " Wallet ")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_accounts.call_count == int(success)


@pytest.mark.parametrize("success", [True, False])
def test_delete_account_renders_service_result(
    monkeypatch,
    success,
):
    result = AccountActionResult(
        success,
        "Account delete result.",
    )
    remove_account_workflow, show_snackbar = patch_account_action(
        monkeypatch,
        "remove_account_workflow",
        result,
    )
    screen = SimpleNamespace(
        close_delete_dialog=Mock(),
        load_accounts=Mock(),
    )

    AccountsScreen.perform_delete_account(screen, 7)

    screen.close_delete_dialog.assert_called_once_with()
    remove_account_workflow.assert_called_once_with(7)
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_accounts.call_count == int(success)


@pytest.mark.parametrize(
    "return_screen",
    ["dashboard", "add_transaction", "transfer"],
)
def test_account_back_returns_to_origin_once(return_screen):
    manager = SimpleNamespace(current="accounts")
    screen = SimpleNamespace(
        manager=manager,
        return_screen=return_screen,
    )

    AccountsScreen.go_back(screen)

    assert manager.current == return_screen
    assert screen.return_screen == "dashboard"


def test_confirm_delete_account_uses_custom_confirmation(
    monkeypatch,
):
    accounts_module = import_module("screens.accounts")
    dialog = SimpleNamespace(open=Mock())
    dialog_factory = Mock(return_value=dialog)
    monkeypatch.setattr(
        accounts_module,
        "EnkryonConfirmationDialog",
        dialog_factory,
    )
    screen = SimpleNamespace(
        perform_delete_account=Mock(),
        close_delete_dialog=Mock(),
    )

    AccountsScreen.confirm_delete_account(screen, 7)

    assert screen.delete_dialog is dialog
    dialog.open.assert_called_once_with()

    dialog_kwargs = dialog_factory.call_args.kwargs

    assert dialog_kwargs["title"] == "Delete Account?"
    assert (
        dialog_kwargs["message"]
        == (
            "Accounts with existing transactions cannot "
            "be deleted. Delete this account?"
        )
    )

    dialog_kwargs["confirm_callback"]()
    dialog_kwargs["cancel_callback"]()

    screen.perform_delete_account.assert_called_once_with(7)
    screen.close_delete_dialog.assert_called_once_with()
