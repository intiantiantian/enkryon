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
    reconcile_callback = ObjectProperty(None, allownone=True)

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

    def reconcile(self):
        if not self.reconcile_callback:
            return

        self.dismiss()
        self.reconcile_callback()

    def disable(self):
        if not self.disable_callback:
            return

        success = self.disable_callback(
            self.ids.effective_date_input.text,
        )
        if success:
            self.dismiss()


class InterestReconciliationDialog(EnkryonOverlay):
    account_name = StringProperty("")
    estimated_text = StringProperty("₱ 0.00")
    accrual_count_text = StringProperty("0 estimated days")
    actual_amount_text = StringProperty("")
    credit_date_text = StringProperty("")
    category_name = StringProperty("Select Income category")
    category_id = ObjectProperty(None, allownone=True)
    variance_text = StringProperty("Variance: —")

    save_callback = ObjectProperty(None, allownone=True)
    category_callback = ObjectProperty(None, allownone=True)
    preview_callback = ObjectProperty(None, allownone=True)

    max_height = NumericProperty(dp(580))
    vertical_margin = NumericProperty(dp(12))

    def calculate_height(self, available_height):
        usable_height = max(
            0,
            available_height - (2 * self.vertical_margin),
        )
        return min(self.max_height, usable_height)

    def select_category(self):
        if self.category_callback:
            self.category_callback(self)

    def set_category(self, category_id, category_name):
        self.category_id = category_id
        self.category_name = category_name

    def refresh_preview(self, credit_date_text=None):
        if not self.preview_callback:
            return
        if credit_date_text is None:
            credit_date_text = self.ids.credit_date_input.text
        preview = self.preview_callback(credit_date_text)
        if preview is None:
            return
        count, estimated_text = preview
        self.accrual_count_text = (
            f"{count} estimated day" if count == 1
            else f"{count} estimated days"
        )
        self.estimated_text = estimated_text
        self.update_variance()

    def update_variance(self, actual_amount_text=None):
        from utils.money import format_money, pesos_to_centavos

        if actual_amount_text is None:
            actual_amount_text = self.ids.actual_amount_input.text
        try:
            actual = pesos_to_centavos(actual_amount_text)
            estimated = pesos_to_centavos(
                self.estimated_text.replace("₱", "").replace(",", "").strip()
            )
        except (ValueError, OverflowError):
            self.variance_text = "Variance: —"
            return

        variance = actual - estimated
        if variance == 0:
            self.variance_text = "Variance: ₱ 0.00"
        elif variance > 0:
            self.variance_text = f"Variance: +{format_money(variance)}"
        else:
            self.variance_text = f"Variance: {format_money(variance)}"

    def save(self):
        if not self.save_callback:
            return

        success = self.save_callback(
            self.ids.actual_amount_input.text,
            self.ids.credit_date_input.text,
            self.category_id,
        )
        if success:
            self.dismiss()
