from theme.tokens import Colors, ComponentSize, Radius, hex_to_rgba
from widgets.buttons import (
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    get_filter_button_style,
)


def test_primary_button_style_uses_primary_colors():
    assert PRIMARY_BUTTON_STYLE["background_color"] == hex_to_rgba(
        Colors.BRAND_PRIMARY
    )
    assert PRIMARY_BUTTON_STYLE["text_color"] == hex_to_rgba(
        Colors.TEXT_ON_PRIMARY
    )
    assert PRIMARY_BUTTON_STYLE["height"] == ComponentSize.BUTTON_HEIGHT
    assert PRIMARY_BUTTON_STYLE["radius"] == [Radius.MD, Radius.MD, Radius.MD, Radius.MD]


def test_secondary_button_style_uses_surface_colors():
    assert SECONDARY_BUTTON_STYLE["background_color"] == hex_to_rgba(
        Colors.SURFACE
    )
    assert SECONDARY_BUTTON_STYLE["text_color"] == hex_to_rgba(
        Colors.BRAND_PRIMARY
    )


def test_selected_filter_button_uses_clear_filled_state():
    style = get_filter_button_style(selected=True)

    assert style["background_color"] == hex_to_rgba(
        Colors.BRAND_PRIMARY
    )
    assert style["text_color"] == hex_to_rgba(
        Colors.TEXT_ON_PRIMARY
    )
    assert style["line_width"] == 3


def test_unselected_filter_button_uses_outlined_surface():
    style = get_filter_button_style(selected=False)

    assert style["background_color"] == hex_to_rgba(Colors.SURFACE)
    assert style["text_color"] == hex_to_rgba(Colors.BRAND_PRIMARY)
    assert style["line_width"] == 1.5
