from database.activity_repository import get_activity


def get_empty_activity_state(
    activity_type=None,
    compact=False,
    account_filtered=False,
    advanced_filters_active=False,
):
    if advanced_filters_active:
        return {
            "title": "No matching activity",
            "message": (
                "Try changing or resetting your search and filters."
            ),
        }

    if activity_type == "income":
        return {
            "title": "No income activity",
            "message": "No income matches the current view.",
        }

    if activity_type == "expense":
        return {
            "title": "No expense activity",
            "message": "No expenses match the current view.",
        }

    if activity_type == "transfer":
        return {
            "title": "No transfers",
            "message": "No transfers match the current view.",
        }

    if account_filtered:
        return {
            "title": "No activity for this account",
            "message": "This account does not have any activity yet.",
        }

    if compact:
        return {
            "title": "No activity yet",
            "message": (
                "Add a transaction or transfer to start tracking "
                "your money."
            ),
        }

    return {
        "title": "No activity yet",
        "message": (
            "Add a transaction or transfer to start building "
            "your history."
        ),
    }


def get_activity_for_view(
    account_id=None,
    activity_type=None,
    search_text=None,
    group_id=None,
    category_id=None,
    start_date=None,
    end_date=None,
    limit=None,
):
    return get_activity(
        account_id=account_id,
        activity_type=activity_type,
        search_text=search_text,
        group_id=group_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


def get_activity_list_data(
    account_id=None,
    activity_type=None,
    search_text=None,
    group_id=None,
    category_id=None,
    start_date=None,
    end_date=None,
    limit=None,
    compact_empty_state=False,
):
    activities = get_activity_for_view(
        account_id=account_id,
        activity_type=activity_type,
        search_text=search_text,
        group_id=group_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    advanced_filters_active = any(
        (
            search_text,
            group_id is not None,
            category_id is not None,
            start_date is not None,
            end_date is not None,
        )
    )
    empty_state = get_empty_activity_state(
        activity_type,
        compact_empty_state,
        account_filtered=account_id is not None,
        advanced_filters_active=advanced_filters_active,
    )
    return {
        "activities": activities,
        "empty_state": empty_state,
    }
