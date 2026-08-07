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
        "text: 'Recent Activity'",
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


def test_temporary_transaction_form_uses_explicit_text_status_cues():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "add_transaction.kv"
    ).read_text(encoding="utf-8")
    screen_source = (
        project_root / "screens" / "add_transaction.py"
    ).read_text(encoding="utf-8")
    action_source = (
        project_root / "screens" / "transaction_form_actions.py"
    ).read_text(encoding="utf-8")

    assert "id: posting_status_label" in layout
    assert "id: posting_guidance_label" in layout
    assert "text: 'SAVE AS PENDING'" in layout
    assert "text: 'POST TRANSACTION'" in layout
    assert "on_release: root.save_temporary_transaction()" in layout
    assert "on_release: root.post_transaction()" in layout
    assert "CHOOSE POSTING STATUS" in action_source
    assert 'status_label="PENDING"' in action_source
    assert 'status_label="POSTED"' in action_source
    assert "balances and totals" in action_source
    assert "temporary_action.disabled" in screen_source
    assert "temporary_action.opacity" in screen_source


def test_temporary_activity_card_uses_text_and_confirmation_copy():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "widgets.kv"
    ).read_text(encoding="utf-8")
    card_source = (
        project_root / "widgets" / "transaction_card.py"
    ).read_text(encoding="utf-8")
    actions_source = (
        project_root / "screens" / "transaction_list_actions.py"
    ).read_text(encoding="utf-8")
    normalized_actions = " ".join(
        actions_source.replace('"', "").split()
    )

    assert "id: posting_status_badge" in layout
    assert "id: posting_status_icon" not in layout
    assert "id: posting_status_label" in layout
    assert "id: post_transaction_action" in layout
    assert "icon: 'check-circle-outline'" in layout
    assert '"PENDING" if is_temporary else ""' in card_source
    assert "posting_status_icon" not in card_source
    assert "Post Pending Transaction?" in actions_source
    assert "financially effective immediately" in normalized_actions
    assert "account balance" in normalized_actions
    assert "totals will update" in normalized_actions


def test_pending_activity_filter_uses_explicit_text_in_activity_history():
    project_root = Path(__file__).resolve().parents[1]
    dashboard_layout = (
        project_root / "kv" / "dashboard.kv"
    ).read_text(encoding="utf-8")
    history_layout = (
        project_root / "kv" / "transactions.kv"
    ).read_text(encoding="utf-8")

    assert "id: pending_filter" not in dashboard_layout
    assert "id: transfer_filter" not in dashboard_layout

    assert "id: pending_filter" in history_layout
    assert "text: 'PENDING'" in history_layout
    assert "root.set_transaction_filter('pending')" in history_layout


def test_pass_through_form_uses_explicit_non_color_text_cues():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "transfer.kv"
    ).read_text(encoding="utf-8")
    screen_source = (
        project_root / "screens" / "transfer.py"
    ).read_text(encoding="utf-8")

    assert "text: 'TRANSFER TYPE'" in layout
    assert "text: 'INTERNAL'" in layout
    assert "text: 'PASS-THROUGH'" in layout
    assert "id: transfer_kind_label" in layout
    assert "id: transfer_guidance_label" in layout
    assert "text: 'Counterparty (optional)'" in layout
    assert '"PASS-THROUGH TRANSFER"' in screen_source
    assert '"INTERNAL TRANSFER"' in screen_source
    assert "FROM decreases and TO increases" in screen_source
    assert "Cash → Bank" in screen_source
    assert "not Income" in screen_source
