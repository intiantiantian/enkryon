from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

from screens.action_results import render_action_result


def test_render_action_result_always_shows_message(monkeypatch):
    action_results_module = import_module("screens.action_results")
    show_snackbar = Mock()
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    result = SimpleNamespace(message="Action result.")

    render_action_result(result)

    show_snackbar.assert_called_once_with("Action result.")


def test_render_action_result_skips_callbacks_when_refresh_not_required(
    monkeypatch,
):
    action_results_module = import_module("screens.action_results")
    show_snackbar = Mock()
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    before_refresh = Mock()
    refresh = Mock()
    result = SimpleNamespace(message="Action failed.")

    render_action_result(
        result,
        before_refresh=before_refresh,
        refresh=refresh,
        refresh_required=False,
    )

    show_snackbar.assert_called_once_with("Action failed.")
    before_refresh.assert_not_called()
    refresh.assert_not_called()


def test_render_action_result_runs_callbacks_after_message(monkeypatch):
    action_results_module = import_module("screens.action_results")
    events = []

    def show_snackbar(message):
        events.append(("message", message))

    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    result = SimpleNamespace(message="Action succeeded.")

    render_action_result(
        result,
        before_refresh=lambda: events.append(("before", None)),
        refresh=lambda: events.append(("refresh", None)),
        refresh_required=True,
    )

    assert events == [
        ("message", "Action succeeded."),
        ("before", None),
        ("refresh", None),
    ]


def test_render_action_result_forwards_snackbar_options(
    monkeypatch,
):
    action_results_module = import_module(
        "screens.action_results"
    )
    show_snackbar = Mock()
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    callback = Mock()
    result = SimpleNamespace(message="Action succeeded.")

    render_action_result(
        result,
        snackbar_options={
            "action_text": "UNDO",
            "action_callback": callback,
            "duration": 8,
        },
    )

    show_snackbar.assert_called_once_with(
        "Action succeeded.",
        action_text="UNDO",
        action_callback=callback,
        duration=8,
    )
