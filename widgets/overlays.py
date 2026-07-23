from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.modalview import ModalView
from kivymd.uix.card import MDCard


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
