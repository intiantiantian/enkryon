from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.label import MDLabel

from calendar import monthrange
from datetime import date, time

from kivy.factory import Factory

class CalendarDay(ButtonBehavior, MDLabel):
    day = NumericProperty(0)
    picker = ObjectProperty(None)
    selected = BooleanProperty(False)

class DatePickerDialog(ModalView):

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

class TimePickerDialog(ModalView):

    def __init__(self, callback=None, initial_time=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.scroll_timer = None
        if initial_time:
            self.hour = initial_time.hour % 12 or 12
            self.minute = initial_time.minute
            self.is_pm = initial_time.hour >= 12
        else:
            self.hour = 12
            self.minute = 0
            self.is_pm = False

    def on_pre_open(self):
        self.ids.minute_picker.data = [
            {'text': f'{i:02d}'}
            for i in range(60)
        ]

        self.ids.hour_picker.data = [
            {'text': f'{i:02d}'}
            for i in range(1, 13)
        ]

        self.ids.ampm_picker.data = [
            {'text': 'AM'},
            {'text': 'PM'}
        ]
        
        Clock.schedule_once(lambda dt: self.set_picker_position(), 0.1)

    def set_picker_position(self):

        hour_index = self.hour - 1
        self.ids.hour_picker.scroll_y = self.get_scroll_position(
            hour_index,
            len(self.ids.hour_picker.data)
        )

        minute_index = self.minute
        self.ids.minute_picker.scroll_y = self.get_scroll_position(
            minute_index,
            len(self.ids.minute_picker.data)
        )

        ampm_index = 1 if not self.is_pm else 2
        self.ids.ampm_picker.scroll_y = self.get_scroll_position(
            ampm_index,
            len(self.ids.ampm_picker.data)
        )
    
    def get_scroll_position(self, index, total):
        if total <= 3:
            return 1
        return 1 - (index / (total - 1))

    def check_scroll(self, rv):

        if self.scroll_timer:
            self.scroll_timer.cancel()
            
        self.scroll_timer = Clock.schedule_once(lambda dt: self.get_center_value(rv), .2)

    def get_center_value(self, rv):

        if rv == self.ids.ampm_picker:
            index = round((1 - rv.scroll_y) * (len(rv.data)-1))
        else:
            index = round((1 - rv.scroll_y) * (len(rv.data)-3)) + 1

        value = rv.data[index]['text']

        if rv == self.ids.hour_picker:
            self.hour = int(value)

        elif rv == self.ids.minute_picker:
            self.minute = int(value)

        elif rv == self.ids.ampm_picker:
            self.is_pm = value == 'PM'

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