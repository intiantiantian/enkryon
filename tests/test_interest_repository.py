import sqlite3

from database.account_repository import delete_account, insert_account
from database.interest_repository import (
    EXACT_ACCRUAL_DENOMINATOR,
    delete_interest_accrual,
    delete_interest_profile,
    get_effective_interest_profile,
    get_interest_accrual,
    get_interest_accruals,
    get_interest_profile_by_id,
    get_interest_profiles,
    insert_interest_accrual,
    insert_interest_profile,
    update_interest_accrual_status,
)
from database.records import InterestAccrualRecord, InterestProfileRecord


def create_account(name="Savings"):
    assert insert_account(name) is True
    return 1


def create_profile(
    annual_rate_micros=3_650_000,
    effective_from="2026-08-01",
    enabled=True,
):
    profile_id = insert_interest_profile(
        account_id=1,
        annual_rate_micros=annual_rate_micros,
        effective_from=effective_from,
        enabled=enabled,
    )
    assert profile_id is not False
    return profile_id


def test_profile_round_trip_preserves_rate_snapshot_fields():
    create_account()
    profile_id = create_profile()

    profile = get_interest_profile_by_id(profile_id)

    assert isinstance(profile, InterestProfileRecord)
    assert profile == InterestProfileRecord(
        profile_id=profile_id,
        account_id=1,
        annual_rate_micros=3_650_000,
        day_count_basis=365,
        effective_from="2026-08-01",
        enabled=1,
    )


def test_profile_history_is_effective_dated_and_ordered():
    create_account()
    first_id = create_profile(1_000_000, "2026-08-01")
    second_id = create_profile(2_000_000, "2026-08-15")

    profiles = get_interest_profiles(1)

    assert [profile.profile_id for profile in profiles] == [first_id, second_id]
    assert get_effective_interest_profile(1, "2026-08-14").profile_id == first_id
    assert get_effective_interest_profile(1, "2026-08-15").profile_id == second_id


def test_disabled_effective_row_stops_later_accruals_without_erasing_history():
    create_account()
    first_id = create_profile(1_000_000, "2026-08-01")
    create_profile(1_000_000, "2026-08-10", enabled=False)

    assert get_effective_interest_profile(1, "2026-08-09").profile_id == first_id
    assert get_effective_interest_profile(1, "2026-08-10") is None
    assert get_effective_interest_profile(1, "2026-09-01") is None
    assert len(get_interest_profiles(1)) == 2


def test_profile_rejects_duplicate_effective_date_and_invalid_constraints():
    create_account()
    create_profile()

    assert insert_interest_profile(1, 4_000_000, "2026-08-01") is False
    assert insert_interest_profile(1, -1, "2026-08-02") is False
    assert insert_interest_profile(1, 1_000_000, "08/03/2026") is False
    assert insert_interest_profile(1, 1_000_000, "2026-08-03", enabled=1) is False
    assert insert_interest_profile(999, 1_000_000, "2026-08-03") is False


def test_accrual_round_trip_preserves_exact_whole_and_remainder_components():
    create_account()
    profile_id = create_profile(1_000_000)

    accrual_id = insert_interest_accrual(
        account_id=1,
        interest_profile_id=profile_id,
        accrual_date="2026-08-02",
        closing_balance_centavos=10_000,
        annual_rate_micros=1_000_000,
        accrued_whole_centavos=0,
        accrued_remainder_numerator=10_000_000_000,
    )

    assert accrual_id is not False
    assert get_interest_accrual(1, "2026-08-02") == InterestAccrualRecord(
        accrual_id=accrual_id,
        account_id=1,
        interest_profile_id=profile_id,
        accrual_date="2026-08-02",
        closing_balance_centavos=10_000,
        annual_rate_micros=1_000_000,
        day_count_basis=365,
        accrued_whole_centavos=0,
        accrued_remainder_numerator=10_000_000_000,
        status="estimated",
        posted_transaction_id=None,
    )


def test_accrual_date_is_idempotent_per_account():
    create_account()
    profile_id = create_profile()

    first_id = insert_interest_accrual(
        1, profile_id, "2026-08-02", 1_000_000, 3_650_000, 100, 0
    )
    duplicate = insert_interest_accrual(
        1, profile_id, "2026-08-02", 1_000_000, 3_650_000, 100, 0
    )

    assert first_id is not False
    assert duplicate is False
    assert len(get_interest_accruals(1)) == 1


def test_accruals_are_returned_in_chronological_order_and_filter_by_status():
    create_account()
    profile_id = create_profile()
    later_id = insert_interest_accrual(
        1, profile_id, "2026-08-03", 1_000_000, 3_650_000, 100, 0
    )
    earlier_id = insert_interest_accrual(
        1, profile_id, "2026-08-02", 1_000_000, 3_650_000, 100, 0
    )
    assert update_interest_accrual_status(earlier_id, "ignored") is True

    assert [row.accrual_id for row in get_interest_accruals(1)] == [
        earlier_id,
        later_id,
    ]
    assert [row.accrual_id for row in get_interest_accruals(1, "estimated")] == [
        later_id
    ]


def test_accrual_constraints_reject_invalid_remainder_date_and_foreign_keys():
    create_account()
    profile_id = create_profile(1_000_000)

    assert insert_account("Other") is True
    other_profile_id = insert_interest_profile(
        account_id=2,
        annual_rate_micros=1_000_000,
        effective_from="2026-08-01",
    )
    assert other_profile_id is not False

    assert insert_interest_accrual(
        1,
        profile_id,
        "2026-08-02",
        10_000,
        1_000_000,
        0,
        EXACT_ACCRUAL_DENOMINATOR,
    ) is False
    assert insert_interest_accrual(
        1, profile_id, "08/02/2026", 10_000, 1_000_000, 0, 1
    ) is False
    assert insert_interest_accrual(
        1, 999, "2026-08-02", 10_000, 1_000_000, 0, 1
    ) is False
    assert insert_interest_accrual(
        1, other_profile_id, "2026-08-02", 10_000, 1_000_000, 0, 1
    ) is False
    assert insert_interest_accrual(
        1, profile_id, "2026-08-02", 10_000, 9_999_999, 0, 1
    ) is False


def test_reconciled_status_requires_a_real_posted_transaction_reference():
    create_account()
    profile_id = create_profile(1_000_000)
    accrual_id = insert_interest_accrual(
        1, profile_id, "2026-08-02", 10_000, 1_000_000, 0, 1
    )

    assert update_interest_accrual_status(accrual_id, "reconciled") is False
    assert update_interest_accrual_status(
        accrual_id, "reconciled", posted_transaction_id=999
    ) is False
    assert get_interest_accrual(1, "2026-08-02").status == "estimated"


def test_delete_profile_is_blocked_after_accrual_and_accrual_can_be_deleted():
    create_account()
    profile_id = create_profile(1_000_000)
    accrual_id = insert_interest_accrual(
        1, profile_id, "2026-08-02", 10_000, 1_000_000, 0, 1
    )

    assert delete_interest_profile(profile_id) is False
    assert delete_interest_accrual(accrual_id) is True
    assert delete_interest_profile(profile_id) is True


def test_account_deletion_is_blocked_by_interest_history():
    create_account()
    profile_id = create_profile()

    assert delete_account(1) == (False, "referenced")

    assert delete_interest_profile(profile_id) is True
    assert delete_account(1) == (True, None)
