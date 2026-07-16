import pytest

from utils.money import (
    centavos_to_peso_text,
    format_money,
    format_signed_money,
    pesos_to_centavos,
)

def test_converts_pesos_to_exact_centavos():
    assert pesos_to_centavos("250.75") == 25075
    assert pesos_to_centavos("0.29") == 29


def test_converts_whole_pesos_to_centavos():
    assert pesos_to_centavos("8000") == 800000


def test_rejects_more_than_two_decimal_places():
    with pytest.raises(
        ValueError,
        match="more than two decimal places",
    ):
        pesos_to_centavos("12.345")


def test_rejects_non_finite_amount():
    with pytest.raises(ValueError, match="finite"):
        pesos_to_centavos("NaN")


def test_rejects_amount_outside_sqlite_integer_range():
    with pytest.raises(OverflowError, match="SQLite"):
        pesos_to_centavos("92233720368547758.08")


def test_converts_centavos_to_keypad_text():
    assert centavos_to_peso_text(25075) == "250.75"
    assert centavos_to_peso_text(25000) == "250"
    assert centavos_to_peso_text(1) == "0.01"
    assert centavos_to_peso_text(-1) == "-0.01"


def test_formats_integer_centavos():
    assert format_money(25075) == "₱ 250.75"
    assert format_money(25000) == "₱ 250.00"


def test_formats_negative_centavo_balance():
    assert format_money(-25075) == "-₱ 250.75"


def test_formats_compact_and_signed_centavos():
    assert format_money(
        123_456_789,
        compact=True,
    ) == "₱ 1.23M"
    assert format_signed_money(
        25075,
        "income",
    ) == "+ ₱ 250.75"
    assert format_signed_money(
        25075,
        "expense",
    ) == "- ₱ 250.75"