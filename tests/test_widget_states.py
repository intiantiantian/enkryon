from theme.tokens import Colors, hex_to_rgba
from theme.widget_states import SELECTED_BUTTON_BG, UNSELECTED_BUTTON_BG


def test_selected_button_bg_uses_soft_accent():
    assert SELECTED_BUTTON_BG == hex_to_rgba(Colors.BRAND_ACCENT_SOFT)


def test_unselected_button_bg_uses_surface():
    assert UNSELECTED_BUTTON_BG == hex_to_rgba(Colors.SURFACE)