from kivy.metrics import dp
from kivy.uix.modalview import ModalView
from kivymd.uix.card import MDCard
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)


class EnkryonOverlay(ModalView):
    max_width = NumericProperty(dp(420))
    horizontal_margin = NumericProperty(dp(16))

    def calculate_width(self, available_width):
        usable_width = max(
            0,
            available_width - (2 * self.horizontal_margin),
        )
        return min(self.max_width, usable_width)


class EnkryonOverlayCard(MDCard):
    pass


class EnkryonConfirmationDialog(EnkryonOverlay):
    title = StringProperty("")
    message = StringProperty("")
    confirm_text = StringProperty("Delete")
    cancel_text = StringProperty("Cancel")

    confirm_callback = ObjectProperty(
        None,
        allownone=True,
    )
    cancel_callback = ObjectProperty(
        None,
        allownone=True,
    )

    max_height = NumericProperty(dp(300))
    vertical_margin = NumericProperty(dp(16))

    def calculate_height(self, available_height):
        usable_height = max(
            0,
            available_height - (2 * self.vertical_margin),
        )

        return min(
            self.max_height,
            usable_height,
        )

    def confirm(self):
        if self.confirm_callback:
            self.confirm_callback()

    def cancel(self):
        if self.cancel_callback:
            self.cancel_callback()
        else:
            self.dismiss()


class EnkryonSelectionOption(EnkryonOverlayCard):
    text = StringProperty("")
    is_selected = BooleanProperty(False)
    is_navigation = BooleanProperty(False)
    selection_callback = ObjectProperty(
        None,
        allownone=True,
    )

    def activate(self):
        if self.selection_callback:
            self.selection_callback()


class EnkryonSelectionPanel(EnkryonOverlay):
    title = StringProperty("")
    selected_text = StringProperty("")
    options = ListProperty([])

    max_height = NumericProperty(dp(560))
    vertical_margin = NumericProperty(dp(16))
    panel_chrome_height = NumericProperty(dp(88))
    option_height = NumericProperty(dp(52))
    option_spacing = NumericProperty(dp(4))
    navigation_inset = NumericProperty(dp(12))

    def calculate_height(
        self,
        available_height,
        option_count=None,
    ):
        if option_count is None:
            option_count = len(self.options)

        navigation_count = sum(
            bool(option.get("is_navigation", False))
            for option in self.options
            if isinstance(option, dict)
        )

        options_height = (
            option_count * self.option_height
            + max(0, option_count - 1) * self.option_spacing
            + navigation_count * self.navigation_inset
        )
        content_height = (
            self.panel_chrome_height + options_height
        )
        usable_height = max(
            0,
            available_height - (2 * self.vertical_margin),
        )

        return min(
            self.max_height,
            content_height,
            usable_height,
        )

    def on_open(self):
        self.populate_options()

    def populate_options(self):
        container = self.ids.options_container
        container.clear_widgets()

        for option in self.options:
            container.add_widget(
                EnkryonSelectionOption(
                    text=option["text"],
                    is_selected=option.get(
                        "selected",
                        option["text"] == self.selected_text,
                    ),
                    selection_callback=option.get(
                        "on_release"
                    ),
                    is_navigation=option.get(
                        "is_navigation",
                        False,
                    ),
                )
            )
