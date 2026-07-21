from pathlib import Path

import pytest

from utils.responsive_layout import should_stack_controls


@pytest.mark.parametrize(
    ("width_dp", "font_scale"),
    [
        (320, 1.0),
        (360, 0.9),
        (600, 2.0),
        (400, 1.0),
    ],
)
def test_controls_stack_for_constrained_layouts(
    width_dp,
    font_scale,
):
    assert should_stack_controls(width_dp, font_scale)


def test_controls_share_a_row_on_wide_standard_layout():
    assert not should_stack_controls(600, 1.0)


def test_transaction_selectors_use_responsive_grids():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "add_transaction.kv"
    ).read_text(encoding="utf-8")

    assert layout.count("should_stack_controls(") == 2
    assert layout.count("row_force_default: True") >= 2


def test_dashboard_uses_responsive_grids():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "dashboard.kv"
    ).read_text(encoding="utf-8")

    assert layout.count("should_stack_controls(") == 4
    assert layout.count("row_force_default: True") >= 4
    assert layout.count("shorten_from: 'right'") >= 2


def test_account_cards_constrain_long_names():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "accounts.kv"
    ).read_text(encoding="utf-8")

    account_name_block = layout.split(
        "id: account_name",
        maxsplit=1,
    )[1].split(
        "MDIconButton:",
        maxsplit=1,
    )[0]

    assert "max_lines: 1" in account_name_block
    assert "shorten: True" in account_name_block
    assert "shorten_from: 'right'" in account_name_block


def test_category_cards_constrain_long_names():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "categories.kv"
    ).read_text(encoding="utf-8")

    category_name_block = layout.split(
        "id: category_name",
        maxsplit=1,
    )[1].split(
        "MDIconButton:",
        maxsplit=1,
    )[0]

    group_name_block = layout.split(
        "id: group_name",
        maxsplit=1,
    )[1].split(
        "MDIconButton:",
        maxsplit=1,
    )[0]

    for name_block in (category_name_block, group_name_block):
        assert "text_size: self.size" in name_block
        assert "max_lines: 1" in name_block
        assert "shorten: True" in name_block
        assert "shorten_from: 'right'" in name_block


def test_transaction_list_uses_responsive_filters_and_cards():
    project_root = Path(__file__).resolve().parents[1]
    transactions_layout = (
        project_root / "kv" / "transactions.kv"
    ).read_text(encoding="utf-8")
    widgets_layout = (
        project_root / "kv" / "widgets.kv"
    ).read_text(encoding="utf-8")

    assert transactions_layout.count(
        "should_stack_controls("
    ) == 1
    assert "row_default_height: '44dp'" in transactions_layout
    assert "row_force_default: True" in transactions_layout

    transaction_card = widgets_layout.split(
        "<TransactionCard>",
        maxsplit=1,
    )[1].split(
        "<EmptyState>",
        maxsplit=1,
    )[0]

    assert transaction_card.count(
        "text_size: self.size"
    ) == 6
    assert transaction_card.count("max_lines: 1") == 6
    assert transaction_card.count("shorten: True") == 6
    assert transaction_card.count(
        "shorten_from: 'right'"
    ) == 5
    assert transaction_card.count(
        "shorten_from: 'left'"
    ) == 1


def test_settings_content_remains_scrollable_and_contained():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "settings.kv"
    ).read_text(encoding="utf-8")

    scroll_content = layout.split(
        "ScrollView:",
        maxsplit=1,
    )[1].split(
        "OutlinedCard:",
        maxsplit=1,
    )[0]

    assert "size_hint_y: None" in scroll_content
    assert "height: self.minimum_height" in scroll_content

    clear_data_label = layout.split(
        "text: 'Clear All Data'",
        maxsplit=1,
    )[1]

    assert "text_size: self.width, self.height" in clear_data_label
    assert "max_lines: 1" in clear_data_label
    assert "shorten: True" in clear_data_label
    assert "shorten_from: 'right'" in clear_data_label


def test_add_transaction_account_selector_constrains_long_names():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "add_transaction.kv"
    ).read_text(encoding="utf-8")
    screen_source = (
        project_root / "screens" / "add_transaction.py"
    ).read_text(encoding="utf-8")

    selector_block = layout.split(
        "id: account_selector",
        maxsplit=1,
    )[1].split(
        "id: amount_label",
        maxsplit=1,
    )[0]

    assert "id: account_label" in selector_block
    assert "height: '48dp'" in selector_block
    assert "max_lines: 1" in selector_block
    assert "shorten: True" in selector_block
    assert "shorten_from: 'right'" in selector_block

    assert screen_source.count(
        "self.ids.account_label.text"
    ) == 2
    assert "self.ids.account_selector.text" not in screen_source
