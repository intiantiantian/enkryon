from database.records import TransferRecord
from screens.transfer_form_state import (
    DESTINATION_ACCOUNT_PROMPT,
    SOURCE_ACCOUNT_PROMPT,
    TransferFormState,
)


def test_empty_transfer_form_state_has_prompts_and_current_labels():
    state = TransferFormState.empty(
        date_label="2026-08-04",
        time_label="02:30 PM",
    )

    assert state == TransferFormState(
        amount="0",
        source_account_id=None,
        source_account_name=SOURCE_ACCOUNT_PROMPT,
        destination_account_id=None,
        destination_account_name=DESTINATION_ACCOUNT_PROMPT,
        date_label="2026-08-04",
        time_label="02:30 PM",
        notes="",
        transfer_id=None,
    )


def test_transfer_form_state_maps_transfer_for_editing():
    transfer = TransferRecord(
        transfer_id=17,
        source_account_id=2,
        destination_account_id=3,
        amount_centavos=12345,
        date_time="2026-08-04 19:30:00",
        notes=None,
        source_account_name="Cash",
        destination_account_name="Savings",
    )

    state = TransferFormState.from_transfer(transfer)

    assert state == TransferFormState(
        amount="123.45",
        source_account_id=2,
        source_account_name="Cash",
        destination_account_id=3,
        destination_account_name="Savings",
        date_label="2026-08-04",
        time_label="07:30 PM",
        notes="",
        transfer_id=17,
    )


def test_transfer_form_state_preserves_exact_centavo_amount_for_editing():
    transfer = TransferRecord(
        transfer_id=17,
        source_account_id=2,
        destination_account_id=3,
        amount_centavos=1,
        date_time="2026-08-04 19:30:00",
        notes="Centavo",
        source_account_name="Cash",
        destination_account_name="Savings",
    )

    assert TransferFormState.from_transfer(transfer).amount == "0.01"


def test_transfer_form_state_builds_save_arguments():
    state = TransferFormState(
        amount="123.45",
        source_account_id=2,
        source_account_name="Cash",
        destination_account_id=3,
        destination_account_name="Savings",
        date_label="2026-08-04",
        time_label="07:30 PM",
        notes="Emergency fund",
        transfer_id=17,
    )

    assert state.to_save_arguments() == {
        "source_account_id": 2,
        "destination_account_id": 3,
        "amount": "123.45",
        "date_label": "2026-08-04",
        "time_label": "07:30 PM",
        "notes_label": "Emergency fund",
        "transfer_id": 17,
    }


def test_new_transfer_form_state_builds_save_arguments_without_id():
    state = TransferFormState()

    assert state.to_save_arguments()["transfer_id"] is None


def test_transfer_form_state_selects_and_clears_source_account():
    state = TransferFormState()

    state.select_source_account(2, "Cash")

    assert state.source_account_id == 2
    assert state.source_account_name == "Cash"

    state.clear_source_account_selection()

    assert state.source_account_id is None
    assert state.source_account_name == SOURCE_ACCOUNT_PROMPT


def test_transfer_form_state_selects_and_clears_destination_account():
    state = TransferFormState()

    state.select_destination_account(3, "Savings")

    assert state.destination_account_id == 3
    assert state.destination_account_name == "Savings"

    state.clear_destination_account_selection()

    assert state.destination_account_id is None
    assert state.destination_account_name == DESTINATION_ACCOUNT_PROMPT


def test_transfer_form_state_normalizes_blank_notes():
    state = TransferFormState()

    state.set_notes("   ")
    assert state.notes == ""

    state.set_notes(None)
    assert state.notes == ""

    state.set_notes(" Emergency fund ")
    assert state.notes == " Emergency fund "
