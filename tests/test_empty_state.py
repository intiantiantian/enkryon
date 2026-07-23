from types import SimpleNamespace
from unittest.mock import Mock

from widgets.empty_state import EmptyState

from pathlib import Path


def test_empty_state_performs_configured_action():
    callback = Mock()
    empty_state = SimpleNamespace(action_callback=callback)

    EmptyState.perform_action(empty_state)

    callback.assert_called_once_with()


def test_empty_state_without_action_is_safe():
    empty_state = SimpleNamespace(action_callback=None)

    EmptyState.perform_action(empty_state)


def test_empty_state_uses_primary_action_button():
    widgets_kv = Path("kv/widgets.kv").read_text(
        encoding="utf-8"
    )
    empty_state_rule = widgets_kv.split(
        "<EmptyState>:",
        1,
    )[1]

    assert "EnkryonPrimaryButton:" in empty_state_rule
    assert "EnkryonSecondaryButton:" not in empty_state_rule
