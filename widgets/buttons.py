from kivymd.uix.button import MDRaisedButton

from theme.tokens import Colors, ComponentSize, Radius, hex_to_rgba


PRIMARY_BUTTON_STYLE = {
    "background_color": hex_to_rgba(Colors.BRAND_PRIMARY),
    "text_color": hex_to_rgba(Colors.TEXT_ON_PRIMARY),
    "height": ComponentSize.BUTTON_HEIGHT,
    "radius": [Radius.MD],
}

SECONDARY_BUTTON_STYLE = {
    "background_color": hex_to_rgba(Colors.SURFACE),
    "text_color": hex_to_rgba(Colors.BRAND_PRIMARY),
    "height": ComponentSize.BUTTON_HEIGHT,
    "radius": [Radius.MD],
}


def get_filter_button_colors(selected):
    background_color = (
        Colors.BRAND_ACCENT_SOFT if selected else Colors.SURFACE
    )

    return {
        "background_color": hex_to_rgba(background_color),
        "text_color": hex_to_rgba(Colors.BRAND_PRIMARY),
    }


class EnkryonPrimaryButton(MDRaisedButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = PRIMARY_BUTTON_STYLE["background_color"]
        self.text_color = PRIMARY_BUTTON_STYLE["text_color"]
        self.height = PRIMARY_BUTTON_STYLE["height"]
        self.radius = PRIMARY_BUTTON_STYLE["radius"]


class EnkryonSecondaryButton(MDRaisedButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = SECONDARY_BUTTON_STYLE["background_color"]
        self.text_color = SECONDARY_BUTTON_STYLE["text_color"]
        self.height = SECONDARY_BUTTON_STYLE["height"]
        self.radius = SECONDARY_BUTTON_STYLE["radius"]


class EnkryonFilterButton(MDRaisedButton):
    def __init__(self, selected=False, **kwargs):
        super().__init__(**kwargs)
        self.height = ComponentSize.SMALL_BUTTON_HEIGHT
        self.radius = [Radius.MD]
        self.set_selected(selected)

    def set_selected(self, selected):
        colors = get_filter_button_colors(selected)
        self.md_bg_color = colors["background_color"]
        self.text_color = colors["text_color"]