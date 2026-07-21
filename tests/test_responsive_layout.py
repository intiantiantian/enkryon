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
