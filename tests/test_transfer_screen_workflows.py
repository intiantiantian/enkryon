from datetime import date, time
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from database.records import AccountRecord, TransferRecord
from screens.transfer import TransferScreen
from screens.transfer_form_state import (
    INTERNAL_TRANSFER_KIND,
    PASS_THROUGH_TRANSFER_KIND,
    TransferFormState,
)
from services.transfer_services import TransferSaveResult


def make_transfer_state(**overrides):
    values = {
        "amount": "123.45",
        "source_account_id": 2,
        "source_account_name": "Cash",
        "destination_account_id": 4,
        "destination_account_name": "Savings",
        "date_label": "2026-07-19",
        "time_label": "07:30 PM",
        "notes": "Monthly savings",
        "transfer_id": None,
    }
    values.update(overrides)
    return TransferFormState(**values)


def make_form_ids():
    return SimpleNamespace(
        amount_label=SimpleNamespace(text=""),
        source_account_label=SimpleNamespace(text=""),
        destination_account_label=SimpleNamespace(text=""),
        date_label=SimpleNamespace(text=""),
        time_label=SimpleNamespace(text=""),
        notes_label=SimpleNamespace(
            text="",
            theme_text_color="Custom",
        ),
        counterparty_label=SimpleNamespace(
            text="",
            theme_text_color="Custom",
        ),
        internal_transfer_button=SimpleNamespace(set_selected=Mock()),
        pass_through_transfer_button=SimpleNamespace(set_selected=Mock()),
        transfer_kind_label=SimpleNamespace(text=""),
        transfer_guidance_label=SimpleNamespace(text=""),
    )


def test_transfer_amount_keypad_updates_exact_display_amount():
    screen = SimpleNamespace(
        form_state=TransferFormState(amount="12.3"),
        update_amount_label=Mock(),
    )

    TransferScreen.press_key(screen, "4")

    assert screen.form_state.amount == "12.34"
    screen.update_amount_label.assert_called_once_with()


def test_transfer_clear_resets_amount():
    screen = SimpleNamespace(
        form_state=TransferFormState(amount="12.34"),
        update_amount_label=Mock(),
    )

    TransferScreen.clear(screen)

    assert screen.form_state.amount == "0"
    screen.update_amount_label.assert_called_once_with()


def test_transfer_reset_form_uses_current_date_time(monkeypatch):
    transfer_module = import_module("screens.transfer")
    current_labels = Mock(return_value=("2026-08-04", "05:30 PM"))
    monkeypatch.setattr(
        transfer_module,
        "get_current_transaction_datetime_labels",
        current_labels,
    )
    screen = SimpleNamespace(
        form_state=make_transfer_state(),
        account_creation_role="destination",
        render_form_state=Mock(),
    )

    TransferScreen.reset_form(screen)

    assert screen.form_state == TransferFormState.empty(
        "2026-08-04",
        "05:30 PM",
    )
    assert screen.account_creation_role is None
    screen.render_form_state.assert_called_once_with()


def test_transfer_render_form_state_updates_every_visible_value():
    state = make_transfer_state()
    ids = make_form_ids()
    screen = SimpleNamespace(
        form_state=state,
        ids=ids,
        update_amount_label=Mock(),
        render_transfer_kind_ui=Mock(),
        set_counterparty=Mock(),
        set_notes=Mock(),
    )

    TransferScreen.render_form_state(screen)

    assert ids.source_account_label.text == "Cash"
    assert ids.destination_account_label.text == "Savings"
    assert ids.date_label.text == "2026-07-19"
    assert ids.time_label.text == "07:30 PM"
    screen.update_amount_label.assert_called_once_with()
    screen.render_transfer_kind_ui.assert_called_once_with()
    screen.set_counterparty.assert_called_once_with("")
    screen.set_notes.assert_called_once_with("Monthly savings")


def test_transfer_pre_enter_resets_new_form():
    screen = SimpleNamespace(
        form_state=TransferFormState(transfer_id=None),
        preserve_form_on_next_enter=False,
        reset_form=Mock(),
    )

    TransferScreen.on_pre_enter(screen)

    screen.reset_form.assert_called_once_with()


def test_transfer_pre_enter_preserves_edit_form():
    screen = SimpleNamespace(
        form_state=TransferFormState(transfer_id=17),
        preserve_form_on_next_enter=False,
        reset_form=Mock(),
    )

    TransferScreen.on_pre_enter(screen)

    screen.reset_form.assert_not_called()


def test_transfer_pre_enter_preserves_account_creation_form_once():
    screen = SimpleNamespace(
        form_state=TransferFormState(),
        preserve_form_on_next_enter=True,
        reset_form=Mock(),
        reconcile_preserved_accounts=Mock(),
        render_form_state=Mock(),
    )

    TransferScreen.on_pre_enter(screen)

    assert screen.preserve_form_on_next_enter is False
    screen.reconcile_preserved_accounts.assert_called_once_with()
    screen.render_form_state.assert_called_once_with()
    screen.reset_form.assert_not_called()


def test_reconcile_preserved_accounts_updates_and_clears_selections(
    monkeypatch,
):
    transfer_module = import_module("screens.transfer")
    get_all_accounts = Mock(
        return_value=[AccountRecord(account_id=2, name="Wallet")]
    )
    monkeypatch.setattr(
        transfer_module,
        "get_all_accounts",
        get_all_accounts,
    )
    screen = SimpleNamespace(
        form_state=make_transfer_state(
            source_account_name="Cash",
            destination_account_id=4,
            destination_account_name="Deleted Savings",
        )
    )

    TransferScreen.reconcile_preserved_accounts(screen)

    assert screen.form_state.source_account_id == 2
    assert screen.form_state.source_account_name == "Wallet"
    assert screen.form_state.destination_account_id is None
    assert (
        screen.form_state.destination_account_name
        == "Select Destination Account"
    )
    get_all_accounts.assert_called_once_with()


@pytest.mark.parametrize("role", ["source", "destination"])
def test_transfer_account_menu_lists_accounts_and_creation_action(
    monkeypatch,
    role,
):
    transfer_module = import_module("screens.transfer")
    get_all_accounts = Mock(
        return_value=[
            AccountRecord(account_id=2, name="Cash"),
            AccountRecord(account_id=4, name="Savings"),
            AccountRecord(account_id=9, name="Emergency Fund"),
        ]
    )
    menu = SimpleNamespace(open=Mock())
    menu_factory = Mock(return_value=menu)
    monkeypatch.setattr(
        transfer_module,
        "get_all_accounts",
        get_all_accounts,
    )
    monkeypatch.setattr(
        transfer_module,
        "EnkryonSelectionPanel",
        menu_factory,
    )
    screen = SimpleNamespace(
        ACCOUNT_ROLES=TransferScreen.ACCOUNT_ROLES,
        form_state=make_transfer_state(),
        ids=make_form_ids(),
        select_source_account=Mock(),
        select_destination_account=Mock(),
        open_add_account_screen=Mock(),
    )

    TransferScreen.open_account_menu(screen, role)

    menu.open.assert_called_once_with()
    assert getattr(screen, f"{role}_account_menu") is menu

    panel_options = menu_factory.call_args.kwargs["options"]
    option_names = [option["text"] for option in panel_options]
    assert "Cash" in option_names
    assert "Savings" in option_names
    assert "Emergency Fund" in option_names
    assert option_names[-1] == "Add New Account"

    panel_options[-1]["on_release"]()
    screen.open_add_account_screen.assert_called_once_with(role)


def test_select_source_account_clears_matching_destination():
    state = make_transfer_state(
        source_account_id=None,
        source_account_name="Select Source Account",
        destination_account_id=4,
        destination_account_name="Savings",
    )
    menu = SimpleNamespace(dismiss=Mock())
    screen = SimpleNamespace(
        form_state=state,
        source_account_menu=menu,
        render_form_state=Mock(),
    )

    TransferScreen.select_source_account(screen, 4, "Savings")

    assert state.source_account_id == 4
    assert state.source_account_name == "Savings"
    assert state.destination_account_id is None
    screen.render_form_state.assert_called_once_with()
    menu.dismiss.assert_called_once_with()


def test_select_destination_account_clears_matching_source():
    state = make_transfer_state(
        source_account_id=2,
        source_account_name="Cash",
        destination_account_id=None,
        destination_account_name="Select Destination Account",
    )
    menu = SimpleNamespace(dismiss=Mock())
    screen = SimpleNamespace(
        form_state=state,
        destination_account_menu=menu,
        render_form_state=Mock(),
    )

    TransferScreen.select_destination_account(screen, 2, "Cash")

    assert state.destination_account_id == 2
    assert state.destination_account_name == "Cash"
    assert state.source_account_id is None
    screen.render_form_state.assert_called_once_with()
    menu.dismiss.assert_called_once_with()


def test_open_add_account_screen_preserves_target_role():
    menu = SimpleNamespace(dismiss=Mock())
    accounts_screen = SimpleNamespace(
        return_screen="dashboard",
        account_created_callback=None,
    )
    manager = SimpleNamespace(
        current="transfer",
        get_screen=Mock(return_value=accounts_screen),
    )
    callback = Mock()
    screen = SimpleNamespace(
        ACCOUNT_ROLES=TransferScreen.ACCOUNT_ROLES,
        manager=manager,
        destination_account_menu=menu,
        select_created_account=callback,
    )

    TransferScreen.open_add_account_screen(screen, "destination")

    assert manager.current == "accounts"
    assert screen.preserve_form_on_next_enter is True
    assert screen.account_creation_role == "destination"
    assert accounts_screen.return_screen == "transfer"
    assert accounts_screen.account_created_callback is callback
    menu.dismiss.assert_called_once_with()


def test_select_created_account_uses_requested_role(monkeypatch):
    transfer_module = import_module("screens.transfer")
    monkeypatch.setattr(
        transfer_module,
        "get_all_accounts",
        Mock(
            return_value=[
                AccountRecord(account_id=9, name="Emergency Fund")
            ]
        ),
    )
    state = make_transfer_state(
        destination_account_id=None,
        destination_account_name="Select Destination Account",
    )
    screen = SimpleNamespace(
        account_creation_role="destination",
        form_state=state,
        render_form_state=Mock(),
    )

    TransferScreen.select_created_account(screen, " emergency fund ")

    assert state.destination_account_id == 9
    assert state.destination_account_name == "Emergency Fund"
    assert screen.account_creation_role is None
    screen.render_form_state.assert_called_once_with()


@pytest.mark.parametrize(
    ("success", "expected_destination"),
    [(True, "dashboard"), (False, "transfer")],
)
def test_save_transfer_renders_result_and_navigates_only_on_success(
    monkeypatch,
    success,
    expected_destination,
):
    transfer_module = import_module("screens.transfer")
    result = TransferSaveResult(
        success,
        (
            "Transfer added successfully."
            if success
            else "Transfer could not be added."
        ),
    )
    save_transfer_workflow = Mock(return_value=result)
    render_action_result = Mock()
    monkeypatch.setattr(
        transfer_module,
        "save_transfer_workflow",
        save_transfer_workflow,
    )
    monkeypatch.setattr(
        transfer_module,
        "render_action_result",
        render_action_result,
    )
    dashboard = SimpleNamespace(load_dashboard=Mock())
    manager = SimpleNamespace(
        current="transfer",
        get_screen=Mock(return_value=dashboard),
    )
    state = make_transfer_state(transfer_id=17)
    screen = SimpleNamespace(form_state=state, manager=manager)

    TransferScreen.save_transfer(screen)

    save_transfer_workflow.assert_called_once_with(
        source_account_id=2,
        destination_account_id=4,
        amount="123.45",
        date_label="2026-07-19",
        time_label="07:30 PM",
        notes_label="Monthly savings",
        transfer_id=17,
        transfer_kind="internal",
        counterparty="",
    )
    render_action_result.assert_called_once_with(result)
    assert manager.current == expected_destination

    if success:
        assert state.transfer_id is None
        dashboard.load_dashboard.assert_called_once_with()
        manager.get_screen.assert_called_once_with("dashboard")
    else:
        assert state.transfer_id == 17
        dashboard.load_dashboard.assert_not_called()
        manager.get_screen.assert_not_called()


def test_save_pass_through_forwards_kind_and_counterparty(monkeypatch):
    transfer_module = import_module("screens.transfer")
    result = TransferSaveResult(True, "Transfer added successfully.")
    save_transfer_workflow = Mock(return_value=result)
    monkeypatch.setattr(
        transfer_module,
        "save_transfer_workflow",
        save_transfer_workflow,
    )
    monkeypatch.setattr(
        transfer_module,
        "render_action_result",
        Mock(),
    )
    dashboard = SimpleNamespace(load_dashboard=Mock())
    manager = SimpleNamespace(
        current="transfer",
        get_screen=Mock(return_value=dashboard),
    )
    state = make_transfer_state(
        transfer_kind=PASS_THROUGH_TRANSFER_KIND,
        counterparty="  Alex Rivera  ",
    )
    screen = SimpleNamespace(form_state=state, manager=manager)

    TransferScreen.save_transfer(screen)

    save_transfer_workflow.assert_called_once_with(
        source_account_id=2,
        destination_account_id=4,
        amount="123.45",
        date_label="2026-07-19",
        time_label="07:30 PM",
        notes_label="Monthly savings",
        transfer_id=None,
        transfer_kind="pass_through",
        counterparty="  Alex Rivera  ",
    )
    assert manager.current == "dashboard"


def test_load_transfer_populates_edit_form(monkeypatch):
    transfer_module = import_module("screens.transfer")
    transfer = TransferRecord(
        transfer_id=17,
        source_account_id=2,
        destination_account_id=4,
        amount_centavos=12345,
        date_time="2026-07-19 19:30:00",
        notes="Monthly savings",
        source_account_name="Cash",
        destination_account_name="Savings",
    )
    get_transfer_for_edit = Mock(return_value=transfer)
    monkeypatch.setattr(
        transfer_module,
        "get_transfer_for_edit",
        get_transfer_for_edit,
    )
    screen = SimpleNamespace(render_form_state=Mock())

    TransferScreen.load_transfer(screen, 17)

    assert screen.form_state == TransferFormState.from_transfer(transfer)
    get_transfer_for_edit.assert_called_once_with(17)
    screen.render_form_state.assert_called_once_with()


def test_transfer_date_time_and_notes_update_form():
    ids = make_form_ids()
    state = make_transfer_state(notes="")
    screen = SimpleNamespace(form_state=state, ids=ids)

    TransferScreen.set_date(screen, date(2026, 8, 4))
    TransferScreen.set_time(screen, time(17, 45))
    TransferScreen.set_notes(screen, "  Emergency savings  ")

    assert state.date_label == "2026-08-04"
    assert state.time_label == "05:45 PM"
    assert state.notes == "  Emergency savings  "
    assert ids.date_label.text == "2026-08-04"
    assert ids.time_label.text == "05:45 PM"
    assert ids.notes_label.text == "  Emergency savings  "
    assert ids.notes_label.theme_text_color == "Primary"


def test_transfer_kind_ui_defaults_to_internal():
    ids = make_form_ids()
    screen = SimpleNamespace(
        form_state=make_transfer_state(
            transfer_kind=INTERNAL_TRANSFER_KIND,
        ),
        ids=ids,
        is_pass_through=True,
    )

    TransferScreen.render_transfer_kind_ui(screen)

    assert screen.is_pass_through is False
    ids.internal_transfer_button.set_selected.assert_called_once_with(True)
    ids.pass_through_transfer_button.set_selected.assert_called_once_with(False)
    assert ids.transfer_kind_label.text == "INTERNAL TRANSFER"
    assert "Move your own money" in ids.transfer_guidance_label.text
    assert "not Income or Expense" in ids.transfer_guidance_label.text


def test_transfer_kind_ui_explains_balance_neutral_exchange():
    ids = make_form_ids()
    screen = SimpleNamespace(
        form_state=make_transfer_state(
            transfer_kind=PASS_THROUGH_TRANSFER_KIND,
            counterparty="Alex Rivera",
        ),
        ids=ids,
        is_pass_through=False,
    )

    TransferScreen.render_transfer_kind_ui(screen)

    assert screen.is_pass_through is True
    ids.internal_transfer_button.set_selected.assert_called_once_with(False)
    ids.pass_through_transfer_button.set_selected.assert_called_once_with(True)
    assert ids.transfer_kind_label.text == "PASS-THROUGH TRANSFER"
    assert "complete exchange" in ids.transfer_guidance_label.text
    assert "neither account balance changes" in ids.transfer_guidance_label.text
    assert "not Income or Expense" in ids.transfer_guidance_label.text


def test_select_pass_through_kind_preserves_counterparty_state():
    state = make_transfer_state(counterparty="Alex Rivera")
    screen = SimpleNamespace(
        form_state=state,
        render_transfer_kind_ui=Mock(),
    )

    TransferScreen.select_transfer_kind(screen, PASS_THROUGH_TRANSFER_KIND)

    assert state.transfer_kind == PASS_THROUGH_TRANSFER_KIND
    assert state.counterparty == "Alex Rivera"
    screen.render_transfer_kind_ui.assert_called_once_with()


def test_select_internal_kind_clears_pass_through_counterparty():
    state = make_transfer_state(
        transfer_kind=PASS_THROUGH_TRANSFER_KIND,
        counterparty="Alex Rivera",
    )
    screen = SimpleNamespace(
        form_state=state,
        render_transfer_kind_ui=Mock(),
    )

    TransferScreen.select_transfer_kind(screen, INTERNAL_TRANSFER_KIND)

    assert state.transfer_kind == INTERNAL_TRANSFER_KIND
    assert state.counterparty == ""
    screen.render_transfer_kind_ui.assert_called_once_with()


def test_add_counterparty_opens_optional_input_for_pass_through(monkeypatch):
    transfer_module = import_module("screens.transfer")
    dialog = SimpleNamespace(open=Mock())
    dialog_factory = Mock(return_value=dialog)
    monkeypatch.setattr(transfer_module, "InputDialog", dialog_factory)
    screen = SimpleNamespace(
        form_state=make_transfer_state(
            transfer_kind=PASS_THROUGH_TRANSFER_KIND,
            counterparty="Alex Rivera",
        ),
        set_counterparty=Mock(),
    )

    TransferScreen.add_counterparty(screen)

    dialog_factory.assert_called_once_with(
        title="Counterparty",
        hint_text="Person or organization (optional)",
        text="Alex Rivera",
        callback=screen.set_counterparty,
    )
    dialog.open.assert_called_once_with()


def test_add_counterparty_is_inactive_for_internal_transfer(monkeypatch):
    transfer_module = import_module("screens.transfer")
    dialog_factory = Mock()
    monkeypatch.setattr(transfer_module, "InputDialog", dialog_factory)
    screen = SimpleNamespace(
        form_state=make_transfer_state(
            transfer_kind=INTERNAL_TRANSFER_KIND,
        ),
    )

    TransferScreen.add_counterparty(screen)

    dialog_factory.assert_not_called()


def test_set_counterparty_displays_trimmed_value_but_preserves_input():
    ids = make_form_ids()
    state = make_transfer_state(
        transfer_kind=PASS_THROUGH_TRANSFER_KIND,
        counterparty="",
    )
    screen = SimpleNamespace(form_state=state, ids=ids)

    TransferScreen.set_counterparty(screen, "  Alex Rivera  ")

    assert state.counterparty == "  Alex Rivera  "
    assert ids.counterparty_label.text == "Alex Rivera"
    assert ids.counterparty_label.theme_text_color == "Primary"


def test_set_blank_counterparty_restores_optional_prompt():
    ids = make_form_ids()
    state = make_transfer_state(
        transfer_kind=PASS_THROUGH_TRANSFER_KIND,
        counterparty="Alex Rivera",
    )
    screen = SimpleNamespace(form_state=state, ids=ids)

    TransferScreen.set_counterparty(screen, "   ")

    assert state.counterparty == "   "
    assert ids.counterparty_label.text == "Add counterparty"
    assert ids.counterparty_label.theme_text_color == "Custom"


def test_load_pass_through_transfer_renders_kind_and_counterparty(monkeypatch):
    transfer_module = import_module("screens.transfer")
    transfer = TransferRecord(
        transfer_id=22,
        source_account_id=2,
        destination_account_id=4,
        amount_centavos=100025,
        date_time="2026-08-07 19:30:00",
        notes="Cash-out",
        source_account_name="Cash",
        destination_account_name="Bank",
        transfer_kind=PASS_THROUGH_TRANSFER_KIND,
        counterparty="Alex Rivera",
    )
    monkeypatch.setattr(
        transfer_module,
        "get_transfer_for_edit",
        Mock(return_value=transfer),
    )
    screen = SimpleNamespace(render_form_state=Mock())

    TransferScreen.load_transfer(screen, 22)

    assert screen.form_state.transfer_kind == PASS_THROUGH_TRANSFER_KIND
    assert screen.form_state.counterparty == "Alex Rivera"
    screen.render_form_state.assert_called_once_with()


def test_transfer_back_resets_form_and_returns_to_dashboard():
    manager = SimpleNamespace(current="transfer")
    screen = SimpleNamespace(
        manager=manager,
        reset_form=Mock(),
    )

    TransferScreen.go_to_dashboard(screen)

    screen.reset_form.assert_called_once_with()
    assert manager.current == "dashboard"


def test_transfer_rejects_unknown_account_role():
    screen = SimpleNamespace(ACCOUNT_ROLES=TransferScreen.ACCOUNT_ROLES)

    with pytest.raises(ValueError, match="Unknown transfer account role"):
        TransferScreen.open_account_menu(screen, "other")
