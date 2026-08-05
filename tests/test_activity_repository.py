from datetime import date

from database.account_repository import insert_account
from database.activity_repository import get_activity
from database.category_group_repository import insert_category_group
from database.category_repository import insert_category
from database.transaction_repository import insert_transaction
from database.transfer_repository import insert_transfer


def seed_activity():
    assert insert_account("Cash") is True
    assert insert_account("Savings") is True
    assert insert_account("Wallet") is True
    assert insert_category_group("Salary", "income") == (True, None)
    assert insert_category_group("Food", "expense") == (True, None)
    assert insert_category(1, "Paycheck") == (True, None)
    assert insert_category(2, "Lunch") == (True, None)

    assert insert_transaction(
        1,
        100_000,
        1,
        "2026-08-01 09:00:00",
        "August salary",
    ) is True
    assert insert_transfer(
        1,
        2,
        25_025,
        "2026-08-02 10:00:00",
        "Emergency fund",
    ) is True
    assert insert_transaction(
        2,
        1_250,
        2,
        "2026-08-03 11:00:00",
        "Team lunch",
    ) is True


def activity_identity(activity):
    return activity.record_type, activity.record_id


def test_combined_activity_is_newest_first_across_record_types():
    seed_activity()

    activities = get_activity()

    assert [activity_identity(row) for row in activities] == [
        ("transaction", 2),
        ("transfer", 1),
        ("transaction", 1),
    ]
    assert [row.activity_type for row in activities] == [
        "expense",
        "transfer",
        "income",
    ]
    assert [row.posting_status for row in activities] == [
        "posted",
        "posted",
        "posted",
    ]


def test_activity_includes_temporary_transaction_status():
    seed_activity()
    assert insert_transaction(
        1,
        2_500,
        2,
        "2026-08-04 12:00:00",
        "Planned meal",
        posting_status="temporary",
    ) is True

    activities = get_activity()

    temporary = activities[0]
    assert temporary.record_type == "transaction"
    assert temporary.activity_type == "expense"
    assert temporary.posting_status == "temporary"


def test_transfer_activity_uses_posted_status_for_shared_card_contract():
    seed_activity()

    transfer = next(
        activity
        for activity in get_activity()
        if activity.record_type == "transfer"
    )

    assert transfer.posting_status == "posted"


def test_activity_limit_applies_after_combining_record_types():
    seed_activity()

    assert [
        activity_identity(row)
        for row in get_activity(limit=2)
    ] == [
        ("transaction", 2),
        ("transfer", 1),
    ]


def test_account_filter_includes_both_transfer_directions():
    seed_activity()

    source_activity = get_activity(account_id=1)
    destination_activity = get_activity(account_id=2)

    source_transfer = next(
        row for row in source_activity
        if row.record_type == "transfer"
    )
    destination_transfer = next(
        row for row in destination_activity
        if row.record_type == "transfer"
    )

    assert source_transfer.direction == "outgoing"
    assert destination_transfer.direction == "incoming"
    assert source_transfer.source_account_name == "Cash"
    assert source_transfer.destination_account_name == "Savings"
    assert all(
        row.direction == "neutral"
        for row in get_activity()
        if row.record_type == "transfer"
    )


def test_activity_type_filters_keep_transfers_semantically_separate():
    seed_activity()

    assert [
        row.activity_type for row in get_activity(activity_type="income")
    ] == ["income"]
    assert [
        row.activity_type for row in get_activity(activity_type="expense")
    ] == ["expense"]
    assert [
        row.activity_type for row in get_activity(activity_type="transfer")
    ] == ["transfer"]


def test_search_matches_transfer_notes_and_either_account():
    seed_activity()

    assert [
        row.record_type for row in get_activity(search_text="Emergency")
    ] == ["transfer"]
    assert [
        row.record_type for row in get_activity(search_text="Cash")
    ] == ["transfer", "transaction"]
    assert [
        row.record_type for row in get_activity(search_text="Savings")
    ] == ["transaction", "transfer"]


def test_search_treats_sql_wildcards_as_literal_characters():
    seed_activity()
    assert insert_transfer(
        2,
        3,
        100,
        "2026-08-04 12:00:00",
        "Goal 100%_done",
    ) is True

    matches = get_activity(search_text="100%_done")

    assert [activity_identity(row) for row in matches] == [
        ("transfer", 2)
    ]


def test_category_filters_exclude_transfer_records():
    seed_activity()

    assert [
        row.activity_type for row in get_activity(group_id=2)
    ] == ["expense"]
    assert [
        row.activity_type for row in get_activity(category_id=1)
    ] == ["income"]


def test_date_filters_apply_to_transactions_and_transfers():
    seed_activity()

    activities = get_activity(
        start_date=date(2026, 8, 2),
        end_date=date(2026, 8, 2),
    )

    assert [activity_identity(row) for row in activities] == [
        ("transfer", 1)
    ]
