from pathlib import Path

import pytest

from utils.responsive_layout import should_stack_controls


@pytest.mark.parametrize(
    ("width_dp", "font_scale"),
    [
        (320, 1.0),
        (359, 0.9),
        (600, 2.0),
        (400, 3.0),
    ],
)
def test_controls_stack_for_constrained_layouts(
    width_dp,
    font_scale,
):
    assert should_stack_controls(width_dp, font_scale)


def test_controls_share_a_row_on_wide_standard_layout():
    assert not should_stack_controls(360, 0.9)
    assert not should_stack_controls(400, 1.0)
    assert not should_stack_controls(600, 1.0)


def test_transaction_form_controls_use_responsive_grids():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "add_transaction.kv"
    ).read_text(encoding="utf-8")

    assert layout.count("should_stack_controls(") == 3
    assert layout.count("row_force_default: True") >= 2


def test_transfer_controls_stack_and_grow_for_enlarged_fonts():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "transfer.kv"
    ).read_text(encoding="utf-8")

    assert layout.count("should_stack_controls(") == 2
    assert layout.count("row_force_default: True") == 2
    assert layout.count("max(1, Metrics.fontscale)") >= 5
    assert "height: self.minimum_height" in layout
    assert "do_scroll_x: False" in layout


def test_transfer_account_selectors_constrain_long_names():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "transfer.kv"
    ).read_text(encoding="utf-8")

    for label_id in (
        "source_account_label",
        "destination_account_label",
    ):
        label_block = layout.split(
            f"id: {label_id}",
            maxsplit=1,
        )[1].split(
            "theme_text_color:",
            maxsplit=1,
        )[0]

        assert "max_lines: 1" in label_block
        assert "shorten: True" in label_block
        assert "shorten_from: 'right'" in label_block


def test_transfer_screen_uses_shared_spacing_and_touch_targets():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "transfer.kv"
    ).read_text(encoding="utf-8")

    scroll_content = layout.split(
        "id: transfer_scroll_content",
        maxsplit=1,
    )[1]
    account_grid = layout.split(
        "id: transfer_account_selectors",
        maxsplit=1,
    )[1].split(
        "id: source_account_selector",
        maxsplit=1,
    )[0]
    date_grid = layout.split(
        "id: transfer_datetime_selectors",
        maxsplit=1,
    )[1].split(
        "id: date_selector",
        maxsplit=1,
    )[0]

    assert "padding: '16dp'" in scroll_content
    assert "spacing: '12dp'" in scroll_content
    assert "row_default_height: dp(88)" in account_grid
    assert "row_default_height: dp(64)" in date_grid
    assert "height: dp(56) * max(1, Metrics.fontscale)" in layout


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
    ) == 2
    assert "row_default_height: '44dp'" in transactions_layout
    assert "row_force_default: True" in transactions_layout

    transaction_card = widgets_layout.split(
        "<TransactionCard>",
        maxsplit=1,
    )[1].split(
        "<TransactionHistoryCard>:",
        maxsplit=1,
    )[0]
    transaction_history_card = widgets_layout.split(
        "<TransactionHistoryCard>:",
        maxsplit=1,
    )[1].split(
        "<EmptyState>",
        maxsplit=1,
    )[0]

    assert transaction_card.count(
        "text_size: self.size"
    ) == 8
    assert transaction_card.count("max_lines: 1") == 7
    assert transaction_card.count("shorten: True") == 7
    assert transaction_card.count(
        "shorten_from: 'right'"
    ) == 6
    assert transaction_card.count(
        "shorten_from: 'left'"
    ) == 1
    assert "size_hint: .9, None" in transaction_card
    assert "size_hint: .8, None" in transaction_card
    assert "size_hint: 1.1, None" in transaction_card
    assert "spacing: '8dp'" in transaction_card
    assert transaction_card.count("pos_hint: {'top': 1}") == 3
    assert transaction_card.count("adaptive_height: True") == 10
    assert transaction_card.count("spacing: '4dp'") == 3
    assert (
        "height: root.fixed_height or self.minimum_height"
        in transaction_card
    )

    assert "RecycleView:" in transactions_layout
    assert (
        "viewclass: 'TransactionHistoryCard'"
        in transactions_layout
    )
    assert "RecycleBoxLayout:" in transactions_layout
    assert (
        "id: transactions_recycle_view"
        in transactions_layout
    )
    assert (
        "id: transaction_empty_state_container"
        in transactions_layout
    )
    assert "id: transactions_container" not in transactions_layout
    assert (
        "dp(88) * max(1, Metrics.fontscale)"
        in transactions_layout
    )
    assert (
        "fixed_height: dp(88) * max(1, Metrics.fontscale)"
        in transaction_history_card
    )
    assert "\n    height:" not in transaction_history_card
    assert "id: posting_status_badge" in transaction_card
    assert "id: posting_status_icon" not in transaction_card
    assert "height: self.minimum_height if root.is_temporary else 0" in (
        transaction_card
    )
    assert "id: post_transaction_action" in transaction_card
    assert "width: dp(48) if root.is_temporary else 0" in (
        transaction_card
    )
    assert "disabled: not root.is_temporary" in transaction_card

    amount_block = transaction_card.split(
        "id: amount",
        maxsplit=1,
    )[1].split(
        "BoxLayout:",
        maxsplit=1,
    )[0]

    assert "font_size: '14sp'" in amount_block


def test_transaction_search_controls_fit_small_widths():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "transactions.kv"
    ).read_text(encoding="utf-8")
    search_controls = layout.split(
        "id: transaction_search",
        maxsplit=1,
    )[1].split(
        "GridLayout:",
        maxsplit=1,
    )[0]
    clear_button = search_controls.split(
        "text: 'CLEAR'",
        maxsplit=1,
    )[1]
    search_field = search_controls.split(
        "EnkryonPrimaryButton:",
        maxsplit=1,
    )[0]

    assert "hint_text: 'Search activity'" in search_controls
    assert "size_hint_x: 1" in search_controls
    assert "text: 'CLEAR'" in search_controls
    assert "width: '88dp'" in search_controls
    assert "height: '48dp'" in search_controls
    assert "on_text:" in search_controls
    assert "pos_hint: {'center_y': .5}" in search_field
    assert (
        "pos_hint: {'center_y': .5 - dp(4) / "
        "(search_controls.height - search_controls.padding[1] - "
        "search_controls.padding[3])}"
        in clear_button
    )


def test_dashboard_and_history_separate_primary_and_secondary_filters():
    project_root = Path(__file__).resolve().parents[1]
    dashboard_layout = (
        project_root / "kv" / "dashboard.kv"
    ).read_text(encoding="utf-8")
    history_layout = (
        project_root / "kv" / "transactions.kv"
    ).read_text(encoding="utf-8")

    assert "id: all_filter" in dashboard_layout
    assert "id: income_filter" in dashboard_layout
    assert "id: expense_filter" in dashboard_layout
    assert "id: transfer_filter" not in dashboard_layout
    assert "id: pending_filter" not in dashboard_layout
    assert "else 3" in dashboard_layout

    primary_filters = history_layout.split(
        "id: primary_activity_filters",
        maxsplit=1,
    )[1].split(
        "id: secondary_activity_filters",
        maxsplit=1,
    )[0]
    secondary_filters = history_layout.split(
        "id: secondary_activity_filters",
        maxsplit=1,
    )[1].split(
        "ScrollView:",
        maxsplit=1,
    )[0]

    assert "id: all_filter" in primary_filters
    assert "id: income_filter" in primary_filters
    assert "id: expense_filter" in primary_filters
    assert "id: transfer_filter" not in primary_filters
    assert "id: pending_filter" not in primary_filters
    assert "else 3" in primary_filters

    assert "id: transfer_filter" in secondary_filters
    assert "text: 'TRANSFER'" in secondary_filters
    assert "id: pending_filter" in secondary_filters
    assert "text: 'PENDING'" in secondary_filters
    assert "else 2" in secondary_filters


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
        'text: "Clear All Data"',
        maxsplit=1,
    )[1]

    assert "text_size: self.width, None" in clear_data_label
    assert "height: self.texture_size[1]" in clear_data_label
    assert "shorten: True" not in clear_data_label
    assert "shorten_from:" not in clear_data_label


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


def test_add_transaction_uses_consistent_spacing_and_balanced_widths():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "add_transaction.kv"
    ).read_text(encoding="utf-8")

    scroll_content = layout.split(
        "ScrollView:",
        maxsplit=1,
    )[1]
    filter_row = layout.split(
        "id: income_button",
        maxsplit=1,
    )[0].rsplit(
        "BoxLayout:",
        maxsplit=1,
    )[1]
    amount_card = layout.split(
        "OutlinedCard:",
        maxsplit=1,
    )[1].split(
        "GridLayout:",
        maxsplit=1,
    )[0]
    selector_card = layout.split(
        "id: keypad_container",
        maxsplit=1,
    )[1].split(
        "id: group_selector",
        maxsplit=1,
    )[0]
    notes_card = layout.split(
        "text: 'Notes'",
        maxsplit=1,
    )[0].rsplit(
        "OutlinedCard:",
        maxsplit=1,
    )[1]

    assert "padding: '16dp'" in scroll_content
    assert "spacing: '12dp'" in scroll_content
    assert "padding: '8dp'" in filter_row
    assert "spacing: '8dp'" in filter_row
    assert 'padding: "16dp"' in amount_card
    assert 'spacing: "12dp"' in amount_card
    assert amount_card.count("size_hint_x: 1") == 2
    assert "padding: '16dp'" in selector_card
    assert "spacing: '12dp'" in selector_card
    assert "padding: dp(16)" in notes_card
    assert "spacing: '8dp'" in notes_card
    assert "padding: 20" not in layout
    assert "spacing: 15" not in layout
    assert "padding: '20dp'" not in layout
    assert "spacing: '20dp'" not in layout


def test_dashboard_summary_row_grows_with_font_scale():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "dashboard.kv"
    ).read_text(encoding="utf-8")

    summary_grid = layout.split(
        "GridLayout:",
        maxsplit=1,
    )[1].split(
        "EnkryonPrimaryButton:",
        maxsplit=1,
    )[0]

    assert (
        "row_default_height: dp(200) * max(1, Metrics.fontscale)"
        in summary_grid
    )


def test_dashboard_balance_scales_to_supported_amount_width():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "dashboard.kv"
    ).read_text(encoding="utf-8")

    balance_card = layout.split(
        "id: eye_button",
        maxsplit=1,
    )[1].split(
        "\n                BoxLayout:",
        maxsplit=1,
    )[0]

    assert "padding: '16dp'" in balance_card
    assert (
        "font_size: min(sp(42), self.width / "
        "max(len(self.text) * .58, 1))"
        in balance_card
    )
    assert "shorten: True" in balance_card
    assert "shorten_from: 'left'" in balance_card


def test_dashboard_primary_actions_use_shared_button_height():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "dashboard.kv"
    ).read_text(encoding="utf-8")

    for label in (
        "+ Add Transaction",
        "Transfer Funds",
        "Manage Accounts",
        "Manage Categories",
    ):
        button_rule = layout.split(
            f"text: '{label}'",
            maxsplit=1,
        )[0].rsplit(
            "EnkryonPrimaryButton:",
            maxsplit=1,
        )[1]

        assert "size_hint: 1, None" in button_rule

    actions_start = layout.index("id: dashboard_actions")
    actions_end = layout.index(
        "row_default_height: '144dp'",
        actions_start,
    )
    action_group = layout[actions_start:actions_end]

    assert (
        "cols: 1 if should_stack_controls("
        "Window.width / dp(1), Metrics.fontscale) else 2"
        in action_group
    )
    assert "height: self.minimum_height" in action_group
    assert "row_default_height: '48dp'" in action_group
    assert "row_force_default: True" in action_group
    assert "spacing: '5dp'" in action_group
    assert action_group.count("EnkryonPrimaryButton:") == 4

    action_labels = [
        "text: '+ Add Transaction'",
        "text: 'Transfer Funds'",
        "text: 'Manage Accounts'",
        "text: 'Manage Categories'",
    ]
    positions = [
        action_group.index(label)
        for label in action_labels
    ]

    assert positions == sorted(positions)


def test_transaction_advanced_filters_scroll_on_small_widths():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "transactions.kv"
    ).read_text(encoding="utf-8")

    advanced_filters = layout.split(
        "id: advanced_filter_scroll",
        maxsplit=1,
    )[1].split(
        "id: active_filter_summary",
        maxsplit=1,
    )[0]

    assert "do_scroll_x: True" in advanced_filters
    assert "do_scroll_y: False" in advanced_filters
    assert "size_hint_x: None" in advanced_filters
    assert "width: self.minimum_width" in advanced_filters

    selector_ids = (
        "account_filter",
        "group_filter",
        "category_filter",
        "start_date_filter",
        "end_date_filter",
    )

    for index, selector_id in enumerate(selector_ids):
        selector = advanced_filters.split(
            f"id: {selector_id}",
            maxsplit=1,
        )[1]

        if index < len(selector_ids) - 1:
            selector = selector.split(
                f"id: {selector_ids[index + 1]}",
                maxsplit=1,
            )[0]

        assert (
            "height: root.ids.all_filter.height"
            in selector
        )
        assert (
            "font_size: root.ids.all_filter.font_size"
            in selector
        )
        assert "pos_hint: {'center_y': .5}" in selector


    active_summary = layout.split(
        "id: active_filter_summary",
        maxsplit=1,
    )[1].split(
        "ScrollView:",
        maxsplit=1,
    )[0]

    assert "id: active_filters_label" in active_summary
    assert "text: 'RESET ALL'" in active_summary
    assert "width: '104dp'" in active_summary
    assert "height: '48dp'" in active_summary


def test_add_transaction_posting_actions_stack_and_grow_with_font_scale():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "add_transaction.kv"
    ).read_text(encoding="utf-8")

    action_group = layout.split(
        "id: transaction_actions",
        maxsplit=1,
    )[1]

    assert "should_stack_controls(" in action_group
    assert "height: self.minimum_height" in action_group
    assert "row_force_default: True" in action_group
    assert "dp(48) * max(1, Metrics.fontscale)" in action_group
    assert "id: temporary_action" in action_group
    assert "id: post_action" in action_group
    assert action_group.count("size_hint: 1, None") >= 2


def test_add_transaction_header_and_guidance_fit_enlarged_text():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "add_transaction.kv"
    ).read_text(encoding="utf-8")

    header = layout.split(
        "BoxLayout:",
        maxsplit=2,
    )[2].split(
        "Widget:",
        maxsplit=1,
    )[0]
    guidance = layout.split(
        "id: posting_status_card",
        maxsplit=1,
    )[1].split(
        "OutlinedCard:",
        maxsplit=1,
    )[0]

    assert "dp(64) * max(1, Metrics.fontscale)" in header
    assert "id: screen_title" in header
    assert "max_lines: 1" in header
    assert "shorten: True" in header
    assert "icon: 'content-save'" not in header
    assert guidance.count("height: self.texture_size[1]") == 2
    assert guidance.count("text_size: self.width, None") == 2
