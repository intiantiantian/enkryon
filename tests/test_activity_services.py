from datetime import date
from unittest.mock import Mock

from services import activity_services


def test_activity_view_forwards_every_repository_filter(monkeypatch):
    expected = [object()]
    get_activity = Mock(return_value=expected)
    monkeypatch.setattr(
        activity_services,
        "get_activity",
        get_activity,
    )
    start_date = date(2026, 8, 1)
    end_date = date(2026, 8, 4)

    result = activity_services.get_activity_for_view(
        account_id=2,
        activity_type="transfer",
        search_text="fund",
        group_id=None,
        category_id=None,
        start_date=start_date,
        end_date=end_date,
        limit=3,
    )

    assert result is expected
    get_activity.assert_called_once_with(
        account_id=2,
        activity_type="transfer",
        search_text="fund",
        group_id=None,
        category_id=None,
        start_date=start_date,
        end_date=end_date,
        limit=3,
    )


def test_activity_list_data_combines_records_and_empty_state(monkeypatch):
    activities = [object()]
    get_activity_for_view = Mock(return_value=activities)
    get_empty_activity_state = Mock(return_value={"title": "Empty"})
    monkeypatch.setattr(
        activity_services,
        "get_activity_for_view",
        get_activity_for_view,
    )
    monkeypatch.setattr(
        activity_services,
        "get_empty_activity_state",
        get_empty_activity_state,
    )

    result = activity_services.get_activity_list_data(
        account_id=2,
        activity_type="transfer",
        search_text="fund",
        compact_empty_state=True,
    )

    assert result == {
        "activities": activities,
        "empty_state": {"title": "Empty"},
    }
    get_activity_for_view.assert_called_once_with(
        account_id=2,
        activity_type="transfer",
        search_text="fund",
        group_id=None,
        category_id=None,
        start_date=None,
        end_date=None,
        limit=None,
    )
    get_empty_activity_state.assert_called_once_with(
        "transfer",
        True,
        account_filtered=True,
        advanced_filters_active=True,
    )


def test_transfer_empty_state_is_specific_and_recoverable():
    assert activity_services.get_empty_activity_state(
        "transfer"
    ) == {
        "title": "No transfers",
        "message": "No transfers match the current view.",
    }


def test_advanced_filters_take_priority_in_empty_state():
    assert activity_services.get_empty_activity_state(
        "transfer",
        advanced_filters_active=True,
    )["title"] == "No matching activity"
