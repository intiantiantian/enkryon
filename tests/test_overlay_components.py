from datetime import date, time
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from widgets.date_time_pickers import (
    DatePickerDialog,
    TimePickerDialog,
)
from widgets.input_dialog import InputDialog


def test_input_dialog_saves_trimmed_text_before_dismiss():
    events = Mock()
    callback = Mock()
    dismiss = Mock()
    events.attach_mock(callback, "callback")
    events.attach_mock(dismiss, "dismiss")
    dialog = SimpleNamespace(
        ids=SimpleNamespace(
            input=SimpleNamespace(text="  Emergency Fund  "),
        ),
        callback=callback,
        dismiss=dismiss,
    )

    InputDialog.save(dialog)

    assert events.mock_calls == [
        call.callback("Emergency Fund"),
        call.dismiss(),
    ]


def test_input_dialog_cancel_dismisses_without_callback():
    callback = Mock()
    dismiss = Mock()
    dialog = SimpleNamespace(
        callback=callback,
        dismiss=dismiss,
    )

    InputDialog.cancel(dialog)

    callback.assert_not_called()
    dismiss.assert_called_once_with()


def test_date_picker_returns_selected_date_before_dismiss():
    events = Mock()
    callback = Mock()
    dismiss = Mock()
    events.attach_mock(callback, "callback")
    events.attach_mock(dismiss, "dismiss")
    picker = SimpleNamespace(
        current_year=2026,
        current_month=7,
        selected_day=1,
        callback=callback,
        dismiss=dismiss,
    )

    DatePickerDialog.select_day(
        picker,
        SimpleNamespace(day=23),
    )

    assert picker.selected_day == 23
    assert events.mock_calls == [
        call.callback(date(2026, 7, 23)),
        call.dismiss(),
    ]


def test_date_picker_previous_month_wraps_to_previous_year():
    picker = SimpleNamespace(
        current_month=1,
        current_year=2026,
        build_calendar=Mock(),
    )

    DatePickerDialog.previous_month(picker)

    assert picker.current_month == 12
    assert picker.current_year == 2025
    picker.build_calendar.assert_called_once_with()


def test_date_picker_next_month_wraps_to_next_year():
    picker = SimpleNamespace(
        current_month=12,
        current_year=2026,
        build_calendar=Mock(),
    )

    DatePickerDialog.next_month(picker)

    assert picker.current_month == 1
    assert picker.current_year == 2027
    picker.build_calendar.assert_called_once_with()


@pytest.mark.parametrize(
    ("hour", "minute", "is_pm", "expected"),
    [
        (12, 5, False, time(0, 5)),
        (12, 5, True, time(12, 5)),
        (3, 45, False, time(3, 45)),
        (3, 45, True, time(15, 45)),
    ],
)
def test_time_picker_converts_twelve_hour_value_before_dismiss(
    hour,
    minute,
    is_pm,
    expected,
):
    events = Mock()
    callback = Mock()
    dismiss = Mock()
    events.attach_mock(callback, "callback")
    events.attach_mock(dismiss, "dismiss")
    picker = SimpleNamespace(
        hour=hour,
        minute=minute,
        is_pm=is_pm,
        callback=callback,
        dismiss=dismiss,
    )

    TimePickerDialog.confirm(picker)

    assert events.mock_calls == [
        call.callback(expected),
        call.dismiss(),
    ]
    