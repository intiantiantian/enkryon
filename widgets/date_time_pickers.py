from kivy.uix.modalview import ModalView

from calendar import monthrange
from datetime import date, time

from kivy.factory import Factory

class DatePickerDialog(ModalView):

    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)

        self.callback = callback

        today = date.today()

        self.current_year = today.year
        self.current_month = today.month
        self.selected_day = today.day

    def on_open(self):

        self.ids.previous.ids.icon.icon = "chevron-left"
        self.ids.next.ids.icon.icon = "chevron-right"

        self.ids.previous.bind(on_release=lambda *_: self.previous_month())
        self.ids.next.bind(on_release=lambda *_: self.next_month())

        self.build_weekdays()
        self.build_calendar()

        self.ids.cancel.bind(
            on_release=lambda *_: self.dismiss()
        )

        self.ids.ok.bind(
            on_release=lambda *_: self.confirm()
        )

    def build_weekdays(self):

        self.ids.weekday_grid.clear_widgets()

        for day in ("Mon","Tue","Wed","Thu","Fri","Sat","Sun"):
            card = Factory.CalendarDay()
            card.ripple_behavior = False
            card.md_bg_color = (0,0,0,0)
            card.ids.label.bold = True
            card.ids.label.text = day
            self.ids.weekday_grid.add_widget(card)

    def build_calendar(self):

        self.ids.calendar_grid.clear_widgets()

        self.ids.month_label.text = (
            date(self.current_year,self.current_month,1)
            .strftime("%B %Y")
        )

        first_weekday, days = monthrange(
            self.current_year,
            self.current_month
        )

        for _ in range(first_weekday):

            self.ids.calendar_grid.add_widget(Factory.CalendarDay())

        for day in range(1, days + 1):

            card = Factory.CalendarDay()
            card.ids.label.text = str(day)
            card.bind(
                on_release=lambda _, d=day: self.select_day(d)
            )
            self.ids.calendar_grid.add_widget(card)

    def select_day(self, day):
        self.selected_day = day
        print(day)

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

    def confirm(self):

        selected = date(
            self.current_year,
            self.current_month,
            self.selected_day
        )

        if self.callback:
            self.callback(selected)

        self.dismiss()

class TimePickerDialog(ModalView):

    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)

        self.callback = callback

        self.hour = 12
        self.minute = 0
        self.is_pm = False

    def on_open(self):

        self.ids.hour.ids.up.ids.icon.icon = "chevron-up"
        self.ids.hour.ids.down.ids.icon.icon = "chevron-down"

        self.ids.minute.ids.up.ids.icon.icon = "chevron-up"
        self.ids.minute.ids.down.ids.icon.icon = "chevron-down"

        self.ids.ampm.ids.up.ids.icon.icon = "chevron-up"
        self.ids.ampm.ids.down.ids.icon.icon = "chevron-down"

        self.ids.cancel.bind(
            on_release=lambda *_: self.dismiss()
        )

        self.ids.ok.bind(
            on_release=lambda *_: self.confirm()
        )

        self.ids.hour.ids.up.bind(
            on_release=lambda *_: self.hour_up()
        )

        self.ids.hour.ids.down.bind(
            on_release=lambda *_: self.hour_down()
        )

        self.ids.minute.ids.up.bind(
            on_release=lambda *_: self.minute_up()
        )

        self.ids.minute.ids.down.bind(
            on_release=lambda *_: self.minute_down()
        )

        self.ids.ampm.ids.up.bind(
            on_release=lambda *_: self.toggle_ampm()
        )

        self.ids.ampm.ids.down.bind(
            on_release=lambda *_: self.toggle_ampm()
        )

        self.refresh()

    def refresh(self):

        self.ids.hour.ids.value.text = f"{self.hour:02d}"

        self.ids.minute.ids.value.text = f"{self.minute:02d}"

        self.ids.ampm.ids.value.text = (
            "PM" if self.is_pm else "AM"
        )

    def hour_up(self):

        self.hour += 1

        if self.hour > 12:
            self.hour = 1

        self.refresh()

    def hour_down(self):

        self.hour -= 1

        if self.hour < 1:
            self.hour = 12

        self.refresh()

    def minute_up(self):

        self.minute += 1

        if self.minute > 59:
            self.minute = 0

        self.refresh()

    def minute_down(self):

        self.minute -= 1

        if self.minute < 0:
            self.minute = 59

        self.refresh()

    def toggle_ampm(self):

        self.is_pm = not self.is_pm

        self.refresh()

    def confirm(self):

        hour = self.hour

        if self.is_pm and hour != 12:
            hour += 12

        if not self.is_pm and hour == 12:
            hour = 0

        selected_time = time(hour, self.minute)

        if self.callback:
            self.callback(selected_time)

        self.dismiss()