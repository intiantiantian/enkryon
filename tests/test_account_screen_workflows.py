from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from screens.accounts import AccountsScreen
from services.account_services import AccountActionResult


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
        accounts_module,
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
    )

    AccountsScreen.load_accounts(screen)

    get_accounts_for_view.assert_called_once_with()
    container.clear_widgets.assert_called_once_with()
    empty_state_factory.assert_called_once_with(
        title="No accounts yet",
        message="Tap + to create your first account.",
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
    monkeypatch.setattr(
        accounts_module,
        "get_accounts_for_view",
        get_accounts_for_view,
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
    for card, account in zip(cards, accounts):
        assert card.screen is screen
        card.set_account.assert_called_once_with(account)
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
    screen = SimpleNamespace(load_accounts=Mock())

    AccountsScreen.save_account(screen, " Cash ")

    create_account_workflow.assert_called_once_with(" Cash ")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_accounts.call_count == int(success)


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
        rename_dialog=SimpleNamespace(
            content_cls=SimpleNamespace(text=" Wallet "),
        ),
        close_rename_dialog=Mock(),
        load_accounts=Mock(),
    )

    AccountsScreen.rename_account(screen, 7)

    rename_account_workflow.assert_called_once_with(7, " Wallet ")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.close_rename_dialog.call_count == int(success)
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
