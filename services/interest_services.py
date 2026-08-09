from datetime import date, timedelta
from typing import NamedTuple

from database.interest_repository import (
    EXACT_ACCRUAL_DENOMINATOR,
    get_effective_interest_profile,
    get_interest_accrual,
    get_interest_accruals,
    get_interest_profiles,
    get_posted_closing_balance_centavos,
    insert_interest_accrual,
)
class ExactInterestAmount(NamedTuple):
    whole_centavos: int
    remainder_numerator: int


class InterestEstimateSummary(NamedTuple):
    exact_amount: ExactInterestAmount
    rounded_centavos: int


def _coerce_date(value):
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("Interest dates must be ISO calendar dates.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Interest dates must be ISO calendar dates.") from error
    if parsed.isoformat() != value:
        raise ValueError("Interest dates must be ISO calendar dates.")
    return parsed


def calculate_daily_interest_exact(
    closing_balance_centavos,
    annual_rate_micros,
):
    if type(closing_balance_centavos) is not int:
        raise ValueError("Closing balance must be integer centavos.")
    if type(annual_rate_micros) is not int or annual_rate_micros < 0:
        raise ValueError("APR must be a non-negative scaled integer.")

    if closing_balance_centavos <= 0 or annual_rate_micros == 0:
        return ExactInterestAmount(0, 0)

    numerator = closing_balance_centavos * annual_rate_micros
    whole_centavos, remainder_numerator = divmod(
        numerator,
        EXACT_ACCRUAL_DENOMINATOR,
    )
    return ExactInterestAmount(whole_centavos, remainder_numerator)


def normalize_exact_interest(whole_centavos, remainder_numerator):
    if type(whole_centavos) is not int or whole_centavos < 0:
        raise ValueError("Whole centavos must be a non-negative integer.")
    if type(remainder_numerator) is not int or remainder_numerator < 0:
        raise ValueError("Remainder must be a non-negative integer.")

    carry, remainder = divmod(
        remainder_numerator,
        EXACT_ACCRUAL_DENOMINATOR,
    )
    return ExactInterestAmount(whole_centavos + carry, remainder)


def round_exact_interest_centavos(exact_amount):
    exact_amount = normalize_exact_interest(
        exact_amount.whole_centavos,
        exact_amount.remainder_numerator,
    )
    rounds_up = (
        exact_amount.remainder_numerator * 2
        >= EXACT_ACCRUAL_DENOMINATOR
    )
    return exact_amount.whole_centavos + int(rounds_up)


def summarize_interest_accruals(accruals):
    whole_centavos = 0
    remainder_numerator = 0

    for accrual in accruals:
        whole_centavos += accrual.accrued_whole_centavos
        remainder_numerator += accrual.accrued_remainder_numerator

    exact_amount = normalize_exact_interest(
        whole_centavos,
        remainder_numerator,
    )
    return InterestEstimateSummary(
        exact_amount=exact_amount,
        rounded_centavos=round_exact_interest_centavos(exact_amount),
    )


def calculate_interest_accrual(account_id, accrual_date):
    accrual_date = _coerce_date(accrual_date)
    profile = get_effective_interest_profile(
        account_id,
        accrual_date.isoformat(),
    )
    if profile is None:
        return None

    closing_date = accrual_date - timedelta(days=1)
    closing_balance_centavos = get_posted_closing_balance_centavos(
        account_id,
        closing_date.isoformat(),
    )
    if closing_balance_centavos is False:
        return None

    exact_amount = calculate_daily_interest_exact(
        closing_balance_centavos,
        profile.annual_rate_micros,
    )
    return {
        "account_id": account_id,
        "interest_profile_id": profile.profile_id,
        "accrual_date": accrual_date.isoformat(),
        "closing_balance_centavos": closing_balance_centavos,
        "annual_rate_micros": profile.annual_rate_micros,
        "accrued_whole_centavos": exact_amount.whole_centavos,
        "accrued_remainder_numerator": exact_amount.remainder_numerator,
    }


def generate_interest_accrual(account_id, accrual_date):
    accrual_date = _coerce_date(accrual_date)
    accrual_date_text = accrual_date.isoformat()

    existing = get_interest_accrual(account_id, accrual_date_text)
    if existing is not None:
        return existing

    payload = calculate_interest_accrual(account_id, accrual_date)
    if payload is None:
        return None

    accrual_id = insert_interest_accrual(**payload)
    if accrual_id is False:
        return get_interest_accrual(account_id, accrual_date_text)

    return get_interest_accrual(account_id, accrual_date_text)


def generate_missing_interest_accruals(account_id, through_date):
    through_date = _coerce_date(through_date)
    profiles = get_interest_profiles(account_id)
    if not profiles:
        return []

    start_date = _coerce_date(profiles[0].effective_from)
    if start_date > through_date:
        return []

    from database.interest_repository import (
        get_posted_daily_balance_movements_centavos,
        insert_interest_accruals_batch,
    )

    existing = get_interest_accruals(
        account_id,
        start_date=start_date.isoformat(),
        end_date=through_date.isoformat(),
    )
    existing_dates = {row.accrual_date for row in existing}

    opening_balance = get_posted_closing_balance_centavos(
        account_id,
        (start_date - timedelta(days=1)).isoformat(),
    )
    if opening_balance is False:
        return []

    movements = get_posted_daily_balance_movements_centavos(
        account_id,
        start_date.isoformat(),
        through_date.isoformat(),
    )
    if movements is False:
        return []

    profile_index = -1
    current_profile = None
    current_balance = opening_balance
    rows_to_insert = []
    current_date = start_date

    while current_date <= through_date:
        current_text = current_date.isoformat()
        while (
            profile_index + 1 < len(profiles)
            and profiles[profile_index + 1].effective_from <= current_text
        ):
            profile_index += 1
            current_profile = profiles[profile_index]

        if (
            current_profile is not None
            and current_profile.enabled
            and current_text not in existing_dates
        ):
            exact_amount = calculate_daily_interest_exact(
                current_balance,
                current_profile.annual_rate_micros,
            )
            rows_to_insert.append(
                (
                    account_id,
                    current_profile.profile_id,
                    current_text,
                    current_balance,
                    current_profile.annual_rate_micros,
                    exact_amount.whole_centavos,
                    exact_amount.remainder_numerator,
                )
            )

        current_balance += movements.get(current_text, 0)
        current_date += timedelta(days=1)

    inserted = insert_interest_accruals_batch(rows_to_insert)
    if inserted is False:
        return []

    return get_interest_accruals(
        account_id,
        start_date=start_date.isoformat(),
        end_date=through_date.isoformat(),
    )


def get_interest_estimate_summary(
    account_id,
    start_date=None,
    end_date=None,
    status="estimated",
):
    start_text = (
        _coerce_date(start_date).isoformat()
        if start_date is not None
        else None
    )
    end_text = (
        _coerce_date(end_date).isoformat()
        if end_date is not None
        else None
    )
    accruals = get_interest_accruals(
        account_id,
        status=status,
        start_date=start_text,
        end_date=end_text,
    )
    return summarize_interest_accruals(accruals)


class InterestProfileActionResult(NamedTuple):
    success: bool
    message: str


def save_interest_profile(
    account_id,
    annual_rate_micros,
    effective_from,
    enabled=True,
):
    if type(annual_rate_micros) is not int or annual_rate_micros < 0:
        return InterestProfileActionResult(
            False,
            "APR must be a non-negative percentage.",
        )
    try:
        effective_from = _coerce_date(effective_from).isoformat()
    except ValueError as error:
        return InterestProfileActionResult(False, str(error))

    from database.interest_repository import insert_interest_profile

    profile_id = insert_interest_profile(
        account_id,
        annual_rate_micros,
        effective_from,
        enabled=enabled,
    )
    if profile_id is False:
        return InterestProfileActionResult(
            False,
            "Interest settings could not be saved. Check that the effective date is not already used.",
        )

    if enabled:
        return InterestProfileActionResult(
            True,
            "Daily interest settings saved.",
        )
    return InterestProfileActionResult(
        True,
        "Daily interest disabled from the selected date.",
    )


class InterestRemovalResult(NamedTuple):
    success: bool
    message: str
    removed_profiles: int = 0
    removed_accruals: int = 0


def remove_interest_tracking(account_id):
    """Permanently remove interest-only tracking data for an account.

    Reconciled posted Income transactions remain normal financial records.
    """
    from database.interest_repository import remove_interest_tracking_data

    removed = remove_interest_tracking_data(account_id)
    if removed is False:
        return InterestRemovalResult(
            False,
            "Interest tracking could not be removed. No changes were saved.",
        )

    profile_count, accrual_count = removed
    if profile_count == 0:
        return InterestRemovalResult(
            False,
            "This account has no interest tracking to remove.",
        )

    return InterestRemovalResult(
        True,
        "Daily interest tracking removed. Posted interest Income was kept.",
        removed_profiles=profile_count,
        removed_accruals=accrual_count,
    )


class InterestReconciliationPreview(NamedTuple):
    accrual_count: int
    estimated_centavos: int


class InterestReconciliationResult(NamedTuple):
    success: bool
    message: str
    posted_transaction_id: int | None = None
    accrual_count: int = 0
    estimated_centavos: int = 0
    actual_centavos: int = 0
    variance_centavos: int = 0


def get_interest_reconciliation_preview(account_id, through_date):
    from database.interest_repository import (
        get_reconcilable_interest_accruals,
    )

    through_date = _coerce_date(through_date)
    if through_date > date.today():
        raise ValueError("Credit date cannot be in the future.")
    generate_missing_interest_accruals(account_id, through_date)
    accruals = get_reconcilable_interest_accruals(
        account_id,
        through_date.isoformat(),
    )
    summary = summarize_interest_accruals(accruals)
    return InterestReconciliationPreview(
        accrual_count=len(accruals),
        estimated_centavos=summary.rounded_centavos,
    )


def reconcile_interest_credit(
    *,
    account_id,
    actual_amount_centavos,
    credit_date,
    category_id,
    notes="Bank interest credit",
):
    from database.interest_repository import (
        reconcile_interest_accruals_transaction,
    )

    if type(actual_amount_centavos) is not int or actual_amount_centavos <= 0:
        return InterestReconciliationResult(
            False,
            "Actual credited interest must be greater than zero.",
        )
    if type(category_id) is not int or category_id <= 0:
        return InterestReconciliationResult(
            False,
            "Please select an Income category.",
        )

    try:
        credit_date = _coerce_date(credit_date)
        if credit_date > date.today():
            raise ValueError("Credit date cannot be in the future.")
    except ValueError as error:
        return InterestReconciliationResult(False, str(error))

    preview = get_interest_reconciliation_preview(
        account_id,
        credit_date,
    )
    if preview.accrual_count == 0:
        return InterestReconciliationResult(
            False,
            "There are no estimated interest days to reconcile through this date.",
        )

    result = reconcile_interest_accruals_transaction(
        account_id=account_id,
        through_date=credit_date.isoformat(),
        amount_centavos=actual_amount_centavos,
        category_id=category_id,
        credit_date_time=f"{credit_date.isoformat()} 12:00:00",
        notes=(notes or "Bank interest credit").strip()
        or "Bank interest credit",
    )
    if result is False:
        return InterestReconciliationResult(
            False,
            "Interest credit could not be reconciled. No financial changes were saved.",
        )

    transaction_id, accrual_count = result
    variance_centavos = (
        actual_amount_centavos - preview.estimated_centavos
    )
    return InterestReconciliationResult(
        True,
        "Interest credit reconciled and posted as Income.",
        posted_transaction_id=transaction_id,
        accrual_count=accrual_count,
        estimated_centavos=preview.estimated_centavos,
        actual_centavos=actual_amount_centavos,
        variance_centavos=variance_centavos,
    )
