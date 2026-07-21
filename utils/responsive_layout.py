NARROW_LAYOUT_WIDTH_DP = 480
LARGE_TEXT_SCALE = 1.3


def should_stack_controls(width_dp, font_scale):
    return (
        width_dp < NARROW_LAYOUT_WIDTH_DP
        or font_scale >= LARGE_TEXT_SCALE
    )
