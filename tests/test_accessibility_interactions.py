from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("relative_path", "undersized_rule", "required_rule"),
    [
        (
            "kv/accounts.kv",
            "size: dp(42), dp(42)",
            "size: dp(48), dp(48)",
        ),
        (
            "kv/categories.kv",
            "size: dp(42), dp(42)",
            "size: dp(48), dp(48)",
        ),
        (
            "kv/input_dialog.kv",
            "height: '42dp'",
            "height: '48dp'",
        ),
        (
            "kv/date_time_pickers.kv",
            "height: '42dp'",
            "height: '48dp'",
        ),
    ],
)
def test_primary_custom_controls_meet_touch_target_floor(
    relative_path,
    undersized_rule,
    required_rule,
):
    project_root = Path(__file__).resolve().parents[1]
    source = (
        project_root / relative_path
    ).read_text(encoding="utf-8")

    assert required_rule in source
    assert undersized_rule not in source


def test_filter_buttons_meet_touch_floor_and_show_press_feedback():
    project_root = Path(__file__).resolve().parents[1]
    button_source = (
        project_root / "widgets" / "buttons.py"
    ).read_text(encoding="utf-8")
    dashboard_layout = (
        project_root / "kv" / "dashboard.kv"
    ).read_text(encoding="utf-8")

    assert (
        "self.height = ComponentSize.TOUCH_TARGET"
        in button_source
    )
    assert "self.ripple_alpha = 0.12" in button_source
    assert "self.ripple_alpha = 0\n" not in button_source

    filter_section = dashboard_layout.split(
        "text: 'Recent Transactions'",
        maxsplit=1,
    )[1].split(
        "id: transactions_container",
        maxsplit=1,
    )[0]

    assert "height: '48dp'" in filter_section
