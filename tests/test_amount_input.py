from utils.amount_input import apply_amount_key


def test_digit_replaces_initial_zero():
    assert apply_amount_key("0", "1") == "1"


def test_digits_append_after_first_digit():
    amount = apply_amount_key("0", "1")
    amount = apply_amount_key(amount, "2")

    assert amount == "12"


def test_decimal_can_only_be_added_once():
    amount = apply_amount_key("12", ".")
    amount = apply_amount_key(amount, ".")

    assert amount == "12."


def test_delete_removes_last_character():
    assert apply_amount_key("123", "delete") == "12"


def test_delete_single_digit_returns_zero():
    assert apply_amount_key("1", "delete") == "0"


def test_clear_returns_zero():
    assert apply_amount_key("123", "clear") == "0"


def test_double_zero_does_not_change_initial_zero():
    assert apply_amount_key("0", "00") == "0"


def test_decimal_input_is_limited_to_two_places():
    amount = apply_amount_key("12.", "3")
    amount = apply_amount_key(amount, "4")
    amount = apply_amount_key(amount, "5")

    assert amount == "12.34"


def test_double_zero_respects_decimal_limit():
    assert apply_amount_key("12.3", "00") == "12.30"