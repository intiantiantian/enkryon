from database.records import TransactionDetailRecord
from screens.transaction_form_state import TransactionFormState


def test_empty_transaction_form_state_has_prompts_and_current_labels():
    state = TransactionFormState.empty(
        date_label="2026-07-20",
        time_label="08:15 AM",
    )

    assert state == TransactionFormState(
        amount="0",
        transaction_type=None,
        account_id=None,
        account_name="Select Account",
        group_id=None,
        group_name="No Transaction Type Selected",
        category_id=None,
        category_name="No Category Group Selected",
        date_label="2026-07-20",
        time_label="08:15 AM",
        notes="",
        transaction_id=None,
    )


def test_transaction_form_state_maps_transaction_for_editing():
    transaction = TransactionDetailRecord(
        transaction_id=17,
        account_id=2,
        amount_centavos=12345,
        category_id=8,
        date_time="2026-07-19 19:30:00",
        notes=None,
        account_name="Cash",
        category_name="Dining",
        group_id=5,
        group_name="Food",
        transaction_type="expense",
    )

    state = TransactionFormState.from_transaction(transaction)

    assert state == TransactionFormState(
        amount="123.45",
        transaction_type="expense",
        account_id=2,
        account_name="Cash",
        group_id=5,
        group_name="Food",
        category_id=8,
        category_name="Dining",
        date_label="2026-07-19",
        time_label="07:30 PM",
        notes="",
        transaction_id=17,
    )


def test_transaction_form_state_builds_save_arguments():
    state = TransactionFormState(
        amount="123.45",
        transaction_type="expense",
        account_id=2,
        account_name="Cash",
        group_id=5,
        group_name="Food",
        category_id=8,
        category_name="Dining",
        date_label="2026-07-19",
        time_label="07:30 PM",
        notes="Dinner",
        transaction_id=17,
    )

    assert state.to_save_arguments() == {
        "account_id": 2,
        "amount": "123.45",
        "transaction_type": "expense",
        "category_id": 8,
        "date_label": "2026-07-19",
        "time_label": "07:30 PM",
        "notes_label": "Dinner",
        "transaction_id": 17,
    }
