import pytest

from database.account_repository import insert_account
from database.category_group_repository import insert_category_group
from database.category_repository import insert_category
from database.interest_repository import (
    EXACT_ACCRUAL_DENOMINATOR,
    get_interest_accruals,
    insert_interest_profile,
)
from database.transaction_repository import insert_transaction
from database.transfer_repository import insert_transfer
from services.interest_services import (
    ExactInterestAmount,
    calculate_daily_interest_exact,
    generate_interest_accrual,
    generate_missing_interest_accruals,
    get_interest_estimate_summary,
    round_exact_interest_centavos,
    save_interest_profile,
    summarize_interest_accruals,
)


def seed_ledger():
    assert insert_account("Savings") is True
    assert insert_account("Cash") is True
    assert insert_category_group("Income", "income") == (True, None)
    assert insert_category_group("Expense", "expense") == (True, None)
    assert insert_category(1, "Salary") == (True, None)
    assert insert_category(2, "Food") == (True, None)


def add_profile(rate=3_650_000, effective_from="2026-08-02", enabled=True):
    profile_id = insert_interest_profile(
        1,
        rate,
        effective_from,
        enabled=enabled,
    )
    assert profile_id is not False
    return profile_id


def test_exact_daily_reference_case_is_one_peso_without_float_math():
    exact = calculate_daily_interest_exact(1_000_000, 3_650_000)

    assert exact == ExactInterestAmount(100, 0)
    assert round_exact_interest_centavos(exact) == 100


def test_subcentavo_values_accumulate_before_round_half_up():
    daily = calculate_daily_interest_exact(10_000, 1_000_000)

    assert daily == ExactInterestAmount(0, 10_000_000_000)
    assert round_exact_interest_centavos(daily) == 0

    class Accrual:
        accrued_whole_centavos = daily.whole_centavos
        accrued_remainder_numerator = daily.remainder_numerator

    summary = summarize_interest_accruals([Accrual()] * 4)

    assert summary.exact_amount == ExactInterestAmount(
        1,
        3_500_000_000,
    )
    assert summary.rounded_centavos == 1


def test_round_half_up_boundary_is_exact():
    below_half = ExactInterestAmount(
        0,
        EXACT_ACCRUAL_DENOMINATOR // 2 - 1,
    )
    exact_half = ExactInterestAmount(
        0,
        EXACT_ACCRUAL_DENOMINATOR // 2,
    )

    assert round_exact_interest_centavos(below_half) == 0
    assert round_exact_interest_centavos(exact_half) == 1


def test_zero_negative_and_zero_apr_accrue_zero():
    assert calculate_daily_interest_exact(0, 3_650_000) == (0, 0)
    assert calculate_daily_interest_exact(-10_000, 3_650_000) == (0, 0)
    assert calculate_daily_interest_exact(10_000, 0) == (0, 0)


def test_calculator_rejects_non_integer_financial_inputs():
    with pytest.raises(ValueError):
        calculate_daily_interest_exact(10_000.0, 1_000_000)
    with pytest.raises(ValueError):
        calculate_daily_interest_exact(10_000, 1_000_000.0)
    with pytest.raises(ValueError):
        calculate_daily_interest_exact(10_000, -1)


def test_generation_uses_prior_day_posted_balance_and_excludes_pending():
    seed_ledger()
    add_profile()
    assert insert_transaction(
        1, 1_000_000, 1, "2026-08-01 09:00:00", None
    ) is True
    assert insert_transaction(
        1,
        500_000,
        2,
        "2026-08-01 10:00:00",
        None,
        posting_status="temporary",
    ) is True
    assert insert_transaction(
        1, 999_999, 2, "2026-08-02 00:00:00", None
    ) is True

    accrual = generate_interest_accrual(1, "2026-08-02")

    assert accrual.closing_balance_centavos == 1_000_000
    assert accrual.accrued_whole_centavos == 100
    assert accrual.accrued_remainder_numerator == 0


def test_internal_transfer_changes_basis_but_pass_through_is_neutral():
    seed_ledger()
    add_profile(rate=3_650_000, effective_from="2026-08-03")
    assert insert_transaction(
        1, 1_000_000, 1, "2026-08-01 09:00:00", None
    ) is True
    assert insert_transfer(
        1,
        2,
        200_000,
        "2026-08-02 10:00:00",
        None,
        transfer_kind="internal",
    ) is True
    assert insert_transfer(
        1,
        2,
        400_000,
        "2026-08-02 11:00:00",
        None,
        transfer_kind="pass_through",
        counterparty="Friend",
    ) is True

    accrual = generate_interest_accrual(1, "2026-08-03")

    assert accrual.closing_balance_centavos == 800_000
    assert accrual.accrued_whole_centavos == 80
    assert accrual.accrued_remainder_numerator == 0


def test_effective_dated_rate_changes_are_snapshotted():
    seed_ledger()
    assert insert_transaction(
        1, 1_000_000, 1, "2026-08-01 09:00:00", None
    ) is True
    first_profile = add_profile(3_650_000, "2026-08-02")
    second_profile = add_profile(7_300_000, "2026-08-04")

    rows = generate_missing_interest_accruals(1, "2026-08-04")

    assert [row.interest_profile_id for row in rows] == [
        first_profile,
        first_profile,
        second_profile,
    ]
    assert [row.annual_rate_micros for row in rows] == [
        3_650_000,
        3_650_000,
        7_300_000,
    ]
    assert [row.accrued_whole_centavos for row in rows] == [100, 100, 200]


def test_disabled_rate_period_generates_no_rows_until_reenabled():
    seed_ledger()
    assert insert_transaction(
        1, 1_000_000, 1, "2026-08-01 09:00:00", None
    ) is True
    add_profile(3_650_000, "2026-08-02")
    add_profile(3_650_000, "2026-08-03", enabled=False)
    add_profile(3_650_000, "2026-08-05", enabled=True)

    rows = generate_missing_interest_accruals(1, "2026-08-05")

    assert [row.accrual_date for row in rows] == [
        "2026-08-02",
        "2026-08-05",
    ]


def test_missed_day_generation_is_idempotent():
    seed_ledger()
    assert insert_transaction(
        1, 1_000_000, 1, "2026-08-01 09:00:00", None
    ) is True
    add_profile(3_650_000, "2026-08-02")

    first = generate_missing_interest_accruals(1, "2026-08-05")
    second = generate_missing_interest_accruals(1, "2026-08-05")

    assert [row.accrual_id for row in second] == [
        row.accrual_id for row in first
    ]
    assert len(get_interest_accruals(1)) == 4


def test_existing_accrual_is_not_silently_rewritten_after_ledger_change():
    seed_ledger()
    assert insert_transaction(
        1, 1_000_000, 1, "2026-08-01 09:00:00", None
    ) is True
    add_profile(3_650_000, "2026-08-02")
    original = generate_interest_accrual(1, "2026-08-02")

    assert insert_transaction(
        1, 500_000, 1, "2026-08-01 12:00:00", None
    ) is True
    repeated = generate_interest_accrual(1, "2026-08-02")

    assert repeated == original
    assert repeated.closing_balance_centavos == 1_000_000


def test_february_29_uses_same_actual_365_denominator():
    seed_ledger()
    assert insert_transaction(
        1, 1_000_000, 1, "2028-02-28 09:00:00", None
    ) is True
    add_profile(3_650_000, "2028-02-29")

    accrual = generate_interest_accrual(1, "2028-02-29")

    assert accrual.day_count_basis == 365
    assert accrual.accrued_whole_centavos == 100


def test_estimate_summary_can_limit_date_range_without_rounding_daily_rows():
    seed_ledger()
    assert insert_transaction(
        1, 10_000, 1, "2026-08-01 09:00:00", None
    ) is True
    add_profile(1_000_000, "2026-08-02")
    generate_missing_interest_accruals(1, "2026-08-06")

    summary = get_interest_estimate_summary(
        1,
        start_date="2026-08-03",
        end_date="2026-08-06",
    )

    assert summary.exact_amount == ExactInterestAmount(1, 3_500_000_000)
    assert summary.rounded_centavos == 1


def test_save_interest_profile_creates_enabled_effective_rate():
    seed_ledger()

    result = save_interest_profile(
        1,
        3_650_000,
        "2026-08-09",
        enabled=True,
    )

    assert result.success is True
    rows = get_interest_accruals(1)
    assert rows == []


def test_save_interest_profile_rejects_duplicate_effective_date():
    seed_ledger()
    assert save_interest_profile(1, 3_650_000, "2026-08-09").success

    result = save_interest_profile(1, 4_000_000, "2026-08-09")

    assert result.success is False
    assert "effective date" in result.message


def test_save_interest_profile_can_effectively_disable_future_accruals():
    seed_ledger()
    assert save_interest_profile(1, 3_650_000, "2026-08-09").success

    result = save_interest_profile(
        1,
        0,
        "2026-08-10",
        enabled=False,
    )

    assert result.success is True
    assert "disabled" in result.message.lower()
