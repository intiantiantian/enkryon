from theme.app_theme import apply_app_theme


class FakeTheme:
    theme_style = None
    primary_palette = None
    primary_hue = None
    accent_palette = None
    accent_hue = None


class FakeApp:
    def __init__(self):
        self.theme_cls = FakeTheme()


def test_apply_app_theme_sets_kivymd_theme_values():
    app = FakeApp()

    apply_app_theme(app)

    assert app.theme_cls.theme_style == "Light"
    assert app.theme_cls.primary_palette == "Teal"
    assert app.theme_cls.primary_hue == "800"
    assert app.theme_cls.accent_palette == "Amber"
    assert app.theme_cls.accent_hue == "700"