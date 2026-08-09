from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import NamedTuple

from utils.money import MAX_SQLITE_INTEGER, format_money


RATE_MICROS_PER_PERCENT = Decimal("1000000")


class AccountInterestViewState(NamedTuple):
    enabled: bool
    configured: bool
    apr_text: str
    effective_date_text: str
    day_count_text: str
    today_estimate_text: str
    accumulated_estimate_text: str
    summary_text: str


def parse_apr_micros(value):
    text = (value or "").strip()
    if not text:
        raise ValueError("APR is required.")

    try:
        rate = Decimal(text)
    except (InvalidOperation, ValueError):
        raise ValueError("APR must be a valid percentage.") from None

    if not rate.is_finite() or rate < 0:
        raise ValueError("APR must be a non-negative percentage.")

    scaled = rate * RATE_MICROS_PER_PERCENT
    integral = scaled.to_integral_value()
    if scaled != integral:
        raise ValueError("APR can use at most six decimal places.")

    micros = int(integral)
    if micros > MAX_SQLITE_INTEGER:
        raise ValueError("APR is too large to store safely.")
    return micros


def format_apr_micros(annual_rate_micros):
    if type(annual_rate_micros) is not int or annual_rate_micros < 0:
        raise ValueError("APR must be a non-negative scaled integer.")

    rate = Decimal(annual_rate_micros) / RATE_MICROS_PER_PERCENT
    return format(rate, "f").rstrip("0").rstrip(".") or "0"


def parse_effective_date(value):
    text = (value or "").strip()
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        raise ValueError("Effective date must use YYYY-MM-DD.") from None

    if parsed.isoformat() != text:
        raise ValueError("Effective date must use YYYY-MM-DD.")
    return text



def next_available_effective_date(profiles, start_date=None):
    if start_date is None:
        start_date = date.today()
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)

    used_dates = {profile.effective_from for profile in profiles}
    candidate = start_date
    while candidate.isoformat() in used_dates:
        candidate += timedelta(days=1)
    return candidate.isoformat()

def build_interest_view_state(
    profile,
    today_summary,
    accumulated_summary,
    as_of_date=None,
):
    if as_of_date is None:
        as_of_date = date.today()
    if isinstance(as_of_date, str):
        as_of_date = date.fromisoformat(as_of_date)

    enabled = profile is not None
    apr_text = (
        format_apr_micros(profile.annual_rate_micros)
        if enabled
        else ""
    )
    effective_date_text = (
        profile.effective_from if enabled else as_of_date.isoformat()
    )
    today_text = format_money(today_summary.rounded_centavos)
    accumulated_text = format_money(accumulated_summary.rounded_centavos)

    configured = enabled or accumulated_summary.rounded_centavos != 0

    if enabled:
        summary_text = (
            f"Interest: {apr_text}% APR · accrued {accumulated_text}"
        )
    elif accumulated_summary.rounded_centavos:
        summary_text = f"Interest: Off · accrued {accumulated_text}"
    elif configured:
        summary_text = "Interest: Off"
    else:
        summary_text = "Interest: Not configured"

    return AccountInterestViewState(
        enabled=enabled,
        configured=configured,
        apr_text=apr_text,
        effective_date_text=effective_date_text,
        day_count_text="Actual/365",
        today_estimate_text=today_text,
        accumulated_estimate_text=accumulated_text,
        summary_text=summary_text,
    )


def load_account_interest_view(account_id, as_of_date=None):
    from database.interest_repository import (
        get_effective_interest_profile,
        get_interest_profiles,
    )
    from services.interest_services import (
        InterestEstimateSummary,
        ExactInterestAmount,
        generate_missing_interest_accruals,
        get_interest_estimate_summary,
    )

    if as_of_date is None:
        as_of_date = date.today()
    if isinstance(as_of_date, str):
        as_of_date = date.fromisoformat(as_of_date)

    as_of_text = as_of_date.isoformat()
    profiles = get_interest_profiles(account_id)
    profile = get_effective_interest_profile(account_id, as_of_text)

    zero_summary = InterestEstimateSummary(ExactInterestAmount(0, 0), 0)
    if profiles:
        generate_missing_interest_accruals(account_id, as_of_date)
        accumulated_summary = get_interest_estimate_summary(account_id)
    else:
        accumulated_summary = zero_summary

    next_effective_date = next_available_effective_date(
        profiles,
        as_of_date,
    )

    if profile is None:
        state = build_interest_view_state(
            None,
            zero_summary,
            accumulated_summary,
            as_of_date,
        )
        return state._replace(
            configured=bool(profiles),
            effective_date_text=next_effective_date,
        )

    today_summary = get_interest_estimate_summary(
        account_id,
        start_date=as_of_date,
        end_date=as_of_date,
    )
    state = build_interest_view_state(
        profile,
        today_summary,
        accumulated_summary,
        as_of_date,
    )
    return state._replace(
        configured=bool(profiles),
        effective_date_text=next_effective_date,
    )
