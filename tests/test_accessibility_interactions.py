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
