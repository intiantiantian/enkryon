from pathlib import Path

from types import SimpleNamespace

import pytest

from theme.tokens import Colors, hex_to_rgba
from widgets.transaction_card import TransactionCard


def test_dashboard_totals_use_words_and_semantic_colors():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "dashboard.kv"
    ).read_text(encoding="utf-8")

    income_summary = layout.split(
        "# go to income overview",
        maxsplit=1,
    )[1].split(
        "# go to expense overview",
        maxsplit=1,
    )[0]
    expense_summary = layout.split(
        "# go to expense overview",
        maxsplit=1,
    )[1].split(
        "text: 'Recent Transactions'",
        maxsplit=1,
    )[0]

    income_amount = income_summary.split(
        "id: income_label",
        maxsplit=1,
    )[1]
    expense_amount = expense_summary.split(
        "id: expense_label",
        maxsplit=1,
    )[1]

    assert "text: 'INCOME'" in income_summary
    assert "theme_text_color: 'Custom'" in income_amount
    assert (
        "text_color: get_color_from_hex(Colors.INCOME)"
        in income_amount
    )

    assert "text: 'EXPENSE'" in expense_summary
    assert "theme_text_color: 'Custom'" in expense_amount
    assert (
        "text_color: get_color_from_hex(Colors.EXPENSE)"
        in expense_amount
    )


@pytest.mark.parametrize(
    (
        "transaction_type",
        "expected_icon",
        "expected_label",
        "expected_color",
        "expected_amount",
    ),
    [
        (
            "income",
            "arrow-up",
            "INCOME",
            hex_to_rgba(Colors.INCOME),
            "+ ₱ 25.00",
        ),
        (
            "expense",
            "arrow-down",
            "EXPENSE",
            hex_to_rgba(Colors.EXPENSE),
            "- ₱ 25.00",
        ),
    ],
)
def test_transaction_rows_use_multiple_type_cues(
    transaction_type,
    expected_icon,
    expected_label,
    expected_color,
    expected_amount,
):
    owner_screen = object()
    card = SimpleNamespace(screen=owner_screen)
    transaction = SimpleNamespace(
        transaction_id=17,
        account_name="Cash",
        group_name="Salary",
        category_name="Monthly",
        amount_centavos=2500,
        transaction_type=transaction_type,
        date_time="2026-07-22 17:30:00",
    )

    TransactionCard.set_transaction(card, transaction)

    assert card.transaction_id == 17
    assert card.screen is owner_screen
    assert card.account_name == "Cash"
    assert card.group_name == "Salary"
    assert card.category_name == "Monthly"
    assert card.transaction_type_icon == expected_icon
    assert card.transaction_type_label == expected_label
    assert card.amount_text == expected_amount
    assert card.date_time_text == "2026-07-22 05:30 PM"
    assert card.transaction_type_color == expected_color
