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

    current_date = _coerce_date(profiles[0].effective_from)
    if current_date > through_date:
        return []

    generated_or_existing = []
    while current_date <= through_date:
        accrual = generate_interest_accrual(account_id, current_date)
        if accrual is not None:
            generated_or_existing.append(accrual)
        current_date += timedelta(days=1)

    return generated_or_existing


def get_interest_estimate_summary(
    account_id,
    start_date=None,
    end_date=None,
    status="estimated",
):
    accruals = get_interest_accruals(account_id, status=status)

    if start_date is not None:
        start_text = _coerce_date(start_date).isoformat()
        accruals = [
            accrual for accrual in accruals
            if accrual.accrual_date >= start_text
        ]

    if end_date is not None:
        end_text = _coerce_date(end_date).isoformat()
        accruals = [
            accrual for accrual in accruals
            if accrual.accrual_date <= end_text
        ]

    return summarize_interest_accruals(accruals)
