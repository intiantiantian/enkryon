from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton

from theme.tokens import Colors, ComponentSize, Radius, hex_to_rgba


PRIMARY_BUTTON_STYLE = {
    "background_color": hex_to_rgba(Colors.BRAND_PRIMARY),
    "text_color": hex_to_rgba(Colors.TEXT_ON_PRIMARY),
    "height": ComponentSize.BUTTON_HEIGHT,
    "radius": [Radius.MD, Radius.MD, Radius.MD, Radius.MD],
}

SECONDARY_BUTTON_STYLE = {
    "background_color": hex_to_rgba(Colors.SURFACE),
    "text_color": hex_to_rgba(Colors.BRAND_PRIMARY),
    "height": ComponentSize.BUTTON_HEIGHT,
    "radius": [Radius.MD, Radius.MD, Radius.MD, Radius.MD],
}


def get_filter_button_style(selected):
    return {
        "background_color": hex_to_rgba(
            Colors.BRAND_PRIMARY if selected else Colors.SURFACE
        ),
        "text_color": hex_to_rgba(
            Colors.TEXT_ON_PRIMARY
            if selected
            else Colors.BRAND_PRIMARY
        ),
        "line_width": 3 if selected else 1.5,
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

class EnkryonFilterButton(MDRectangleFlatButton):
    def __init__(self, selected=False, **kwargs):
        super().__init__(**kwargs)
        self.height = ComponentSize.TOUCH_TARGET
        self.radius = [Radius.MD, Radius.MD, Radius.MD, Radius.MD]
        self.ripple_alpha = 0.12
        self.line_color = hex_to_rgba(Colors.BRAND_PRIMARY)
        self.set_selected(selected)
        
    def set_selected(self, selected):
        style = get_filter_button_style(selected)
        self.md_bg_color = style["background_color"]
        self.text_color = style["text_color"]
        self.line_width = style["line_width"]
