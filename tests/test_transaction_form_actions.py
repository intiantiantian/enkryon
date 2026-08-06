import pytest

from screens.transaction_form_actions import (
    get_transaction_form_action_state,
)


def test_new_transaction_actions_offer_temporary_and_posting_choices():
    state = get_transaction_form_action_state(
        transaction_id=None,
        posting_status="posted",
    )

    assert state.screen_title == "Add Transaction"
    assert state.status_label == "CHOOSE POSTING STATUS"
    assert "balances and totals" in state.guidance_text
    assert state.temporary_action_text == "SAVE AS PENDING"
    assert state.temporary_action_disabled is False
    assert state.primary_action_text == "POST TRANSACTION"


def test_temporary_edit_actions_preserve_non_posting_status():
    state = get_transaction_form_action_state(
        transaction_id=17,
        posting_status="temporary",
    )

    assert state.screen_title == "Edit Pending Transaction"
    assert state.status_label == "PENDING"
    assert "remain unchanged" in state.guidance_text
    assert state.temporary_action_text == "SAVE PENDING"
    assert state.temporary_action_disabled is False
    assert state.primary_action_text == "POST TRANSACTION"


def test_posted_edit_actions_prevent_reverting_to_temporary():
    state = get_transaction_form_action_state(
        transaction_id=17,
        posting_status="posted",
    )

    assert state.screen_title == "Edit Transaction"
    assert state.status_label == "POSTED"
    assert "cannot return to pending" in state.guidance_text
    assert state.temporary_action_text == "ALREADY POSTED"
    assert state.temporary_action_disabled is True
    assert state.primary_action_text == "SAVE CHANGES"


def test_transaction_form_actions_reject_unknown_status():
    with pytest.raises(ValueError):
        get_transaction_form_action_state(
            transaction_id=17,
            posting_status="pending",
        )
