ZERO_AMOUNT = "0"

DELETE_KEYS = {"delete", "del", "backspace", "⌫"}
CLEAR_KEYS = {"clear", "c"}
DECIMAL_KEYS = {".", "decimal"}


def apply_amount_key(current_amount, key):
    key_text = str(key).strip()
    normalized_key = key_text.lower()

    if normalized_key in CLEAR_KEYS:
        return ZERO_AMOUNT

    if normalized_key in DELETE_KEYS:
        return delete_last_amount_character(current_amount)

    if normalized_key in DECIMAL_KEYS:
        return add_decimal_point(current_amount)

    if not key_text.isdigit():
        return current_amount

    return append_digit(current_amount, key_text)


def append_digit(current_amount, digit):
    if current_amount == ZERO_AMOUNT:
        if digit == "00":
            return ZERO_AMOUNT

        return digit

    return f"{current_amount}{digit}"


def add_decimal_point(current_amount):
    if "." in current_amount:
        return current_amount

    if not current_amount:
        return "0."

    return f"{current_amount}."


def delete_last_amount_character(current_amount):
    if len(current_amount) <= 1:
        return ZERO_AMOUNT

    return current_amount[:-1]