from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)

from .overlays import EnkryonOverlay


class InterestSettingsDialog(EnkryonOverlay):
    account_name = StringProperty("")
    apr_text = StringProperty("")
    effective_date_text = StringProperty("")
    day_count_text = StringProperty("Actual/365")
    today_estimate_text = StringProperty("₱ 0.00")
    accumulated_estimate_text = StringProperty("₱ 0.00")
    is_enabled = BooleanProperty(False)

    save_callback = ObjectProperty(None, allownone=True)
    disable_callback = ObjectProperty(None, allownone=True)

    max_height = NumericProperty(dp(640))
    vertical_margin = NumericProperty(dp(12))

    def calculate_height(self, available_height):
        usable_height = max(
            0,
            available_height - (2 * self.vertical_margin),
        )
        return min(self.max_height, usable_height)

    def save(self):
        if not self.save_callback:
            return

        success = self.save_callback(
            self.ids.apr_input.text,
            self.ids.effective_date_input.text,
        )
        if success:
            self.dismiss()

    def disable(self):
        if not self.disable_callback:
            return

        success = self.disable_callback(
            self.ids.effective_date_input.text,
        )
        if success:
            self.dismiss()
