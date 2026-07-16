from utils.transaction_validation import validate_transaction_form


def test_valid_transaction_form():
    is_valid, message = validate_transaction_form(
        account_id=1,
        amount="100",
        transaction_type="income",
        category_id=1,
    )

    assert is_valid is True
    assert message is None


def test_requires_account():
    is_valid, message = validate_transaction_form(
        account_id=None,
        amount="100",
        transaction_type="income",
        category_id=1,
    )

    assert is_valid is False
    assert message == "Please select an account."


def test_requires_positive_amount():
    is_valid, message = validate_transaction_form(
        account_id=1,
        amount="0",
        transaction_type="income",
        category_id=1,
    )

    assert is_valid is False
    assert message == "Amount cannot be less than or equal to zero."


def test_requires_transaction_type():
    is_valid, message = validate_transaction_form(
        account_id=1,
        amount="100",
        transaction_type=None,
        category_id=1,
    )

    assert is_valid is False
    assert message == "Please select a transaction type."


def test_requires_category():
    is_valid, message = validate_transaction_form(
        account_id=1,
        amount="100",
        transaction_type="expense",
        category_id=None,
    )

    assert is_valid is False
    assert message == "Please select a category."


def test_rejects_more_than_two_decimal_places():
    is_valid, message = validate_transaction_form(
        account_id=1,
        amount="12.345",
        transaction_type="expense",
        category_id=1,
    )

    assert is_valid is False
    assert message == (
        "Please enter a valid amount with up to two decimal places."
    )