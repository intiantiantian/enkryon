from datetime import date, time
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import pytest

from pathlib import Path

from kivy.metrics import dp

from widgets.overlays import (
    EnkryonConfirmationDialog,
    EnkryonOverlay,
    EnkryonSelectionOption,
    EnkryonSelectionPanel,
)
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
    commit_picker_values = Mock()
    events.attach_mock(callback, "callback")
    events.attach_mock(dismiss, "dismiss")
    picker = SimpleNamespace(
        hour=hour,
        minute=minute,
        is_pm=is_pm,
        callback=callback,
        dismiss=dismiss,
        commit_picker_values=commit_picker_values,
    )

    TimePickerDialog.confirm(picker)
    commit_picker_values.assert_called_once_with()

    assert events.mock_calls == [
        call.callback(expected),
        call.dismiss(),
    ]


def test_time_picker_commits_all_visible_values_immediately():
    scroll_timer = Mock()
    hour_picker = object()
    minute_picker = object()
    ampm_picker = object()
    get_center_value = Mock()
    picker = SimpleNamespace(
        scroll_timer=scroll_timer,
        ids=SimpleNamespace(
            hour_picker=hour_picker,
            minute_picker=minute_picker,
            ampm_picker=ampm_picker,
        ),
        get_center_value=get_center_value,
    )

    TimePickerDialog.commit_picker_values(picker)

    scroll_timer.cancel.assert_called_once_with()
    assert picker.scroll_timer is None
    assert get_center_value.mock_calls == [
        call(hour_picker),
        call(minute_picker),
        call(ampm_picker),
    ]


def test_time_picker_reads_committed_value_before_callback():
    callback = Mock()
    picker = SimpleNamespace(
        hour=3,
        minute=45,
        is_pm=True,
        callback=callback,
        dismiss=Mock(),
    )
    picker.commit_picker_values = Mock(
        side_effect=lambda: setattr(picker, "minute", 46)
    )

    TimePickerDialog.confirm(picker)

    callback.assert_called_once_with(time(15, 46))
    picker.dismiss.assert_called_once_with()


def test_overlay_width_preserves_compact_window_margins():
    overlay = SimpleNamespace(
        max_width=dp(420),
        horizontal_margin=dp(16),
    )

    width = EnkryonOverlay.calculate_width(overlay, dp(320))

    assert width == pytest.approx(dp(288))


def test_overlay_width_is_capped_on_wide_windows():
    overlay = SimpleNamespace(
        max_width=dp(420),
        horizontal_margin=dp(16),
    )

    width = EnkryonOverlay.calculate_width(overlay, dp(900))

    assert width == pytest.approx(dp(420))


def test_existing_custom_dialogs_share_overlay_foundation():
    assert issubclass(InputDialog, EnkryonOverlay)
    assert issubclass(DatePickerDialog, EnkryonOverlay)
    assert issubclass(TimePickerDialog, EnkryonOverlay)


def test_shared_overlay_rules_are_loaded_before_dialog_rules():
    project_root = Path(__file__).resolve().parents[1]
    main_source = (project_root / "main.py").read_text()
    overlay_layout = (project_root / "kv" / "overlays.kv").read_text()
    input_layout = (project_root / "kv" / "input_dialog.kv").read_text()
    picker_layout = (
        project_root / "kv" / "date_time_pickers.kv"
    ).read_text()

    overlay_load = "Builder.load_file('kv/overlays.kv')"
    input_load = "Builder.load_file('kv/input_dialog.kv')"

    assert main_source.index(overlay_load) < main_source.index(input_load)
    assert "<EnkryonOverlay>:" in overlay_layout
    assert "<EnkryonOverlayCard>:" in overlay_layout
    assert input_layout.count("EnkryonOverlayCard:") == 1
    assert picker_layout.count("EnkryonOverlayCard:") == 2


def test_time_picker_pre_open_pads_wheels_and_positions_before_frame():
    hour_picker = SimpleNamespace(data=[])
    minute_picker = SimpleNamespace(data=[])
    ampm_picker = SimpleNamespace(data=[])
    set_picker_position = Mock()
    picker = SimpleNamespace(
        ids=SimpleNamespace(
            hour_picker=hour_picker,
            minute_picker=minute_picker,
            ampm_picker=ampm_picker,
        ),
        set_picker_position=set_picker_position,
    )

    with patch(
        "widgets.date_time_pickers.Clock.schedule_once"
    ) as schedule_once:
        TimePickerDialog.on_pre_open(picker)

    assert hour_picker.data[0]["text"] == ""
    assert hour_picker.data[1]["text"] == "01"
    assert hour_picker.data[-2]["text"] == "12"
    assert hour_picker.data[-1]["text"] == ""
    assert minute_picker.data[1]["text"] == "00"
    assert minute_picker.data[-2]["text"] == "59"
    assert [item["text"] for item in ampm_picker.data] == [
        "AM",
        "PM",
    ]
    set_picker_position.assert_called_once_with()
    schedule_once.assert_called_once_with(
        set_picker_position,
        -1,
    )


def test_time_picker_scroll_positions_cover_all_edge_values():
    picker = SimpleNamespace()

    assert TimePickerDialog.get_scroll_position(
        picker, 1, 14
    ) == pytest.approx(1)
    assert TimePickerDialog.get_scroll_position(
        picker, 12, 14
    ) == pytest.approx(0)
    assert TimePickerDialog.get_scroll_position(
        picker, 1, 62
    ) == pytest.approx(1)
    assert TimePickerDialog.get_scroll_position(
        picker, 60, 62
    ) == pytest.approx(0)
    assert TimePickerDialog.get_scroll_position(
        picker, 0, 2, padded=False
    ) == pytest.approx(1)
    assert TimePickerDialog.get_scroll_position(
        picker, 1, 2, padded=False
    ) == pytest.approx(0)


def test_time_picker_snaps_selected_value_to_center():
    hour_picker = SimpleNamespace(
        data=(
            [{"text": ""}]
            + [{"text": f"{i:02d}"} for i in range(1, 13)]
            + [{"text": ""}]
        ),
        scroll_y=0.51,
    )
    picker = SimpleNamespace(
        ids=SimpleNamespace(
            hour_picker=hour_picker,
            minute_picker=object(),
            ampm_picker=object(),
        ),
        hour=1,
        minute=0,
        is_pm=False,
        scroll_timer=Mock(),
        _is_snapping=False,
    )
    picker.get_center_value = lambda rv: (
        TimePickerDialog.get_center_value(picker, rv)
    )
    picker.get_scroll_position = lambda index, total, padded=True: (
        TimePickerDialog.get_scroll_position(
            picker,
            index,
            total,
            padded,
        )
    )

    TimePickerDialog.snap_to_center(picker, hour_picker)

    assert picker.hour == 6
    assert hour_picker.scroll_y == pytest.approx(1 - (5 / 11))
    assert picker.scroll_timer is None
    assert picker._is_snapping is False


def test_time_picker_scroll_debounce_runs_snap():
    old_timer = Mock()
    picker = SimpleNamespace(
        _is_snapping=False,
        scroll_timer=old_timer,
        snap_to_center=Mock(),
    )
    wheel = object()

    with patch(
        "widgets.date_time_pickers.Clock.schedule_once"
    ) as schedule_once:
        TimePickerDialog.check_scroll(picker, wheel)

    old_timer.cancel.assert_called_once_with()
    callback, delay = schedule_once.call_args.args
    assert delay == pytest.approx(0.15)

    callback(0)

    picker.snap_to_center.assert_called_once_with(wheel)


@pytest.mark.parametrize(
    (
        "option_count",
        "available_height",
        "expected_height",
    ),
    [
        (2, dp(800), dp(196)),
        (20, dp(800), dp(560)),
        (20, dp(400), dp(368)),
    ],
)
def test_selection_panel_height_is_responsive(
    option_count,
    available_height,
    expected_height,
):
    panel = SimpleNamespace(
        options=[object()] * option_count,
        max_height=dp(560),
        vertical_margin=dp(16),
        panel_chrome_height=dp(88),
        option_height=dp(52),
        option_spacing=dp(4),
        navigation_inset=dp(12),
    )

    height = EnkryonSelectionPanel.calculate_height(
        panel,
        available_height,
    )

    assert height == pytest.approx(expected_height)


def test_selection_panel_populates_and_marks_selected_option():
    cash_callback = Mock()
    add_callback = Mock()
    container = SimpleNamespace(
        clear_widgets=Mock(),
        add_widget=Mock(),
    )
    panel = SimpleNamespace(
        selected_text="Cash",
        options=[
            {
                "text": "Cash",
                "on_release": cash_callback,
            },
            {
                "text": "Add New Account",
                "is_navigation": True,
                "on_release": add_callback,
            },
        ],
        ids=SimpleNamespace(
            options_container=container,
        ),
    )
    cash_widget = object()
    add_widget = object()

    with patch(
        "widgets.overlays.EnkryonSelectionOption",
        side_effect=[cash_widget, add_widget],
    ) as option_class:
        EnkryonSelectionPanel.populate_options(panel)

    container.clear_widgets.assert_called_once_with()
    assert option_class.mock_calls == [
        call(
            text="Cash",
            is_selected=True,
            is_navigation=False,
            selection_callback=cash_callback,
        ),
        call(
            text="Add New Account",
            is_selected=False,
            is_navigation=True,
            selection_callback=add_callback,
        ),
    ]
    assert container.add_widget.mock_calls == [
        call(cash_widget),
        call(add_widget),
    ]


def test_selection_option_runs_its_callback():
    callback = Mock()
    option = SimpleNamespace(
        selection_callback=callback,
    )

    EnkryonSelectionOption.activate(option)

    callback.assert_called_once_with()


def test_selection_panel_rules_are_registered():
    project_root = Path(__file__).resolve().parents[1]
    overlay_layout = (
        project_root / "kv" / "overlays.kv"
    ).read_text()
    main_source = (
        project_root / "main.py"
    ).read_text()

    assert "<EnkryonSelectionOption>:" in overlay_layout
    assert "<EnkryonSelectionPanel>:" in overlay_layout
    assert "id: options_container" in overlay_layout
    assert "EnkryonSelectionOption," in main_source
    assert "EnkryonSelectionPanel," in main_source


def test_transaction_selectors_use_custom_panels():
    project_root = Path(__file__).resolve().parents[1]
    source = (
        project_root / "screens" / "add_transaction.py"
    ).read_text()

    assert "MDDropdownMenu" not in source
    assert source.count("EnkryonSelectionPanel(") == 3
    assert source.count('"is_navigation": True') == 3


def test_dashboard_selector_uses_custom_panel():
    project_root = Path(__file__).resolve().parents[1]
    source = (
        project_root / "screens" / "dashboard.py"
    ).read_text()

    assert "MDDropdownMenu" not in source
    assert source.count("EnkryonSelectionPanel(") == 1


def test_selection_panel_height_includes_navigation_divider():
    panel = SimpleNamespace(
        options=[
            {"text": "Cash"},
            {
                "text": "Add New Account",
                "is_navigation": True,
            },
        ],
        max_height=dp(560),
        vertical_margin=dp(16),
        panel_chrome_height=dp(88),
        option_height=dp(52),
        option_spacing=dp(4),
        navigation_inset=dp(12),
    )

    height = EnkryonSelectionPanel.calculate_height(
        panel,
        dp(800),
    )

    assert height == pytest.approx(dp(208))


def test_selection_navigation_divider_uses_clear_wrapper():
    project_root = Path(__file__).resolve().parents[1]
    overlay_layout = (
        project_root / "kv" / "overlays.kv"
    ).read_text()

    option_rule = overlay_layout.split(
        "<EnkryonSelectionOption>:",
        1,
    )[1].split(
        "<EnkryonSelectionPanel>:",
        1,
    )[0]

    assert "md_bg_color: 0, 0, 0, 0" in option_rule
    assert (
        "height: dp(12) if root.is_navigation else 0"
        in option_rule
    )
    assert "\n    EnkryonOverlayCard:\n" in option_rule
    assert 'anchor_y: "center"' in option_rule
    assert "size: dp(24), dp(24)" in option_rule
    assert "text_size: self.size" not in option_rule


@pytest.mark.parametrize(
    ("available_height", "expected_height"),
    [
        (dp(800), dp(300)),
        (dp(260), dp(228)),
    ],
)
def test_confirmation_dialog_height_is_responsive(
    available_height,
    expected_height,
):
    dialog = SimpleNamespace(
        max_height=dp(300),
        vertical_margin=dp(16),
    )

    height = EnkryonConfirmationDialog.calculate_height(
        dialog,
        available_height,
    )

    assert height == pytest.approx(expected_height)


def test_confirmation_dialog_routes_callbacks():
    confirm_callback = Mock()
    cancel_callback = Mock()
    dismiss = Mock()
    dialog = SimpleNamespace(
        confirm_callback=confirm_callback,
        cancel_callback=cancel_callback,
        dismiss=dismiss,
    )

    EnkryonConfirmationDialog.confirm(dialog)
    EnkryonConfirmationDialog.cancel(dialog)

    confirm_callback.assert_called_once_with()
    cancel_callback.assert_called_once_with()
    dismiss.assert_not_called()

    dialog.cancel_callback = None
    EnkryonConfirmationDialog.cancel(dialog)

    dismiss.assert_called_once_with()


def test_confirmation_prompts_use_custom_overlay():
    project_root = Path(__file__).resolve().parents[1]
    overlay_layout = (
        project_root / "kv" / "overlays.kv"
    ).read_text()
    main_source = (
        project_root / "main.py"
    ).read_text()
    sources = {
        "accounts": (
            project_root / "screens" / "accounts.py"
        ).read_text(),
        "categories": (
            project_root / "screens" / "categories.py"
        ).read_text(),
        "transactions": (
            project_root
            / "screens"
            / "transaction_list_actions.py"
        ).read_text(),
        "settings": (
            project_root / "screens" / "settings.py"
        ).read_text(),
    }

    assert "<EnkryonConfirmationDialog>:" in overlay_layout
    assert (
        "md_bg_color: get_color_from_hex(Colors.ERROR)"
        in overlay_layout
    )
    assert "EnkryonConfirmationDialog," in main_source

    assert sources["accounts"].count(
        "EnkryonConfirmationDialog("
    ) == 1
    assert sources["categories"].count(
        "EnkryonConfirmationDialog("
    ) == 2
    assert sources["transactions"].count(
        "EnkryonConfirmationDialog("
    ) == 1
    assert sources["settings"].count(
        "EnkryonConfirmationDialog("
    ) == 1

    # Account rename remains for the final input-dialog task.
    assert sources["accounts"].count("MDDialog(") == 1

    for name in (
        "categories",
        "transactions",
        "settings",
    ):
        assert "MDDialog" not in sources[name]
