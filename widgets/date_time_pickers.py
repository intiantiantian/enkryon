from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.label import MDLabel
from kivy.factory import Factory

from calendar import monthrange
from datetime import date, time

from .overlays import EnkryonOverlay


class CalendarDay(ButtonBehavior, MDLabel):
    day = NumericProperty(0)
    picker = ObjectProperty(None)
    selected = BooleanProperty(False)


class DatePickerDialog(EnkryonOverlay):

    day = NumericProperty(0)

    def __init__(self, callback=None, initial_date=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback

        selected = initial_date or date.today()
        
        self.current_month = selected.month
        self.current_year = selected.year

        self.selected_year = selected.year
        self.selected_month = selected.month
        self.selected_day = selected.day

        self.day_widgets = []

        self.build_weekdays()


    def on_pre_open(self):
        if not self.day_widgets:
            self.build_calendar_widgets()
        self.build_calendar()


    def build_weekdays(self):
        self.ids.weekday_grid.clear_widgets()
        for day in ("Mon","Tue","Wed","Thu","Fri","Sat","Sun"):
            card = Factory.CalendarDay()
            card.ripple_behavior = False
            card.md_bg_color = (0, 0, 0, 0)
            card.text = day
            self.ids.weekday_grid.add_widget(card)


    def build_calendar_widgets(self):
        for _ in range(42):
            card = Factory.CalendarDay()
            card.picker = self
            self.day_widgets.append(card)
            self.ids.calendar_grid.add_widget(card)


    def build_calendar(self):
        self.ids.month_label.text = (
            date(self.current_year, self.current_month, 1).strftime('%B %Y')
        )
        first_weekday, days = monthrange(
            self.current_year,
            self.current_month
        )

        day = 1

        for i, card in enumerate(self.day_widgets):
            if first_weekday <= i < first_weekday + days:
                card.day = day
                card.selected = (
                    day == self.selected_day
                    and self.current_month == self.selected_month
                    and self.current_year == self.selected_year
                    )
                card.text = str(day)
                card.disabled = False
                card.ripple_behavior = True
                day += 1

            else:
                card.day = 0
                card.text = ''
                card.disabled = True
                card.ripple_behavior = False


    def select_day(self, day):
        self.selected_day = day.day

        selected = date(
            self.current_year,
            self.current_month,
            self.selected_day
        )

        if self.callback:
            self.callback(selected)

        self.dismiss()


    def previous_month(self):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.build_calendar()


    def next_month(self):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.build_calendar()


class TimePickerDialog(EnkryonOverlay):

    def __init__(self, callback=None, initial_time=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.scroll_timer = None
        self._is_snapping = False
        if initial_time:
            self.hour = initial_time.hour % 12 or 12
            self.minute = initial_time.minute
            self.is_pm = initial_time.hour >= 12
        else:
            self.hour = 12
            self.minute = 0
            self.is_pm = False


    def on_pre_open(self):
        self._is_snapping = True

        try:
            self.ids.minute_picker.data = (
                [{"text": ""}]
                + [{"text": f"{i:02d}"} for i in range(60)]
                + [{"text": ""}]
            )
            self.ids.hour_picker.data = (
                [{"text": ""}]
                + [{"text": f"{i:02d}"} for i in range(1, 13)]
                + [{"text": ""}]
            )
            self.ids.ampm_picker.data = [
                {"text": "AM"},
                {"text": "PM"},
            ]
        finally:
            self._is_snapping = False

        # Position immediately, then correct before the first rendered frame.
        self.set_picker_position()
        Clock.schedule_once(self.set_picker_position, -1)


    def set_picker_position(self, *_):
        self._is_snapping = True

        try:
            hour_picker = self.ids.hour_picker
            minute_picker = self.ids.minute_picker
            ampm_picker = self.ids.ampm_picker

            hour_picker.scroll_y = self.get_scroll_position(
                self.hour,
                len(hour_picker.data),
            )
            minute_picker.scroll_y = self.get_scroll_position(
                self.minute + 1,
                len(minute_picker.data),
            )
            ampm_picker.scroll_y = self.get_scroll_position(
                1 if self.is_pm else 0,
                len(ampm_picker.data),
                padded=False,
            )
        finally:
            self._is_snapping = False


    def get_scroll_position(self, index, total, padded=True):
        if padded:
            steps = total - 3
            if steps <= 0:
                return 1
            return 1 - ((index - 1) / steps)

        steps = total - 1
        if steps <= 0:
            return 1
        return 1 - (index / steps)


    def check_scroll(self, rv):
        if self._is_snapping:
            return

        if self.scroll_timer:
            self.scroll_timer.cancel()

        self.scroll_timer = Clock.schedule_once(
            lambda _: self.snap_to_center(rv),
            0.15,
        )


    def snap_to_center(self, rv):
        self.scroll_timer = None
        index = self.get_center_value(rv)

        self._is_snapping = True

        try:
            rv.scroll_y = self.get_scroll_position(
                index,
                len(rv.data),
                padded=rv is not self.ids.ampm_picker,
            )
        finally:
            self._is_snapping = False


    def get_center_value(self, rv):
        if rv is self.ids.ampm_picker:
            last_index = len(rv.data) - 1
            index = round((1 - rv.scroll_y) * last_index)
            index = max(0, min(index, last_index))
        else:
            last_center_index = len(rv.data) - 2
            index = (
                round((1 - rv.scroll_y) * (len(rv.data) - 3))
                + 1
            )
            index = max(1, min(index, last_center_index))

        value = rv.data[index]["text"]

        if rv is self.ids.hour_picker:
            self.hour = int(value)
        elif rv is self.ids.minute_picker:
            self.minute = int(value)
        elif rv is self.ids.ampm_picker:
            self.is_pm = value == "PM"

        return index


    def commit_picker_values(self):
        if self.scroll_timer:
            self.scroll_timer.cancel()
            self.scroll_timer = None

        self.get_center_value(self.ids.hour_picker)
        self.get_center_value(self.ids.minute_picker)
        self.get_center_value(self.ids.ampm_picker)


    def confirm(self):
        self.commit_picker_values()

        hour = self.hour

        if self.is_pm and hour != 12:
            hour += 12

        if not self.is_pm and hour == 12:
            hour = 0

        selected_time = time(hour, self.minute)

        if self.callback:
            self.callback(selected_time)

        self.dismiss()
