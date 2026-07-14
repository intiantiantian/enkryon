def validate_transaction_form(
    account_id,
    amount,
    transaction_type,
    category_id,
):
    if account_id is None:
        return False, "Please select an account."

    if float(amount) <= 0:
        return False, "Amount cannot be less than or equal to zero."

    if not transaction_type:
        return False, "Please select a transaction type."

    if category_id is None:
        return False, "Please select a category."

    return True, None