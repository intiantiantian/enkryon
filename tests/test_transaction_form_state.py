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
        posting_status="posted",
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
        posting_status="temporary",
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
        posting_status="temporary",
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
        posting_status="temporary",
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
        "posting_status": "temporary",
    }


def test_new_transaction_form_state_builds_save_arguments_without_id():
    state = TransactionFormState()

    assert state.to_save_arguments()["transaction_id"] is None


def test_transaction_form_state_selects_account():
    state = TransactionFormState()

    state.select_account(2, "Cash")

    assert state.account_id == 2
    assert state.account_name == "Cash"


def test_transaction_form_state_clears_account_selection():
    state = TransactionFormState(account_id=2, account_name="Cash")

    state.clear_account_selection()

    assert state.account_id is None
    assert state.account_name == "Select Account"


def test_transaction_form_state_clears_group_and_category_selection():
    state = TransactionFormState(
        group_id=5,
        group_name="Food",
        category_id=8,
        category_name="Dining",
    )

    state.clear_group_selection()

    assert state.group_id is None
    assert state.group_name == "Select Category Group"
    assert state.category_id is None
    assert state.category_name == "No Category Group Selected"


def test_transaction_form_state_clears_category_selection():
    state = TransactionFormState(category_id=8, category_name="Dining")

    state.clear_category_selection()

    assert state.category_id is None
    assert state.category_name == "Select Category"


def test_transaction_type_selection_clears_group_and_category():
    state = TransactionFormState(
        transaction_type="income",
        group_id=5,
        group_name="Salary",
        category_id=8,
        category_name="Wages",
    )

    state.select_transaction_type("expense")

    assert state.transaction_type == "expense"
    assert state.group_id is None
    assert state.group_name == "Select Category Group"
    assert state.category_id is None
    assert state.category_name == "No Category Group Selected"


def test_group_selection_clears_category():
    state = TransactionFormState(
        category_id=8,
        category_name="Dining",
    )

    state.select_group(5, "Food")

    assert state.group_id == 5
    assert state.group_name == "Food"
    assert state.category_id is None
    assert state.category_name == "Select Category"


def test_transaction_form_state_selects_category():
    state = TransactionFormState()

    state.select_category(8, "Dining")

    assert state.category_id == 8
    assert state.category_name == "Dining"


def test_transaction_form_state_normalizes_notes():
    state = TransactionFormState()

    state.set_notes("   ")
    assert state.notes == ""

    state.set_notes(" Dinner ")
    assert state.notes == " Dinner "
