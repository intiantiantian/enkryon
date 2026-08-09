from types import SimpleNamespace

import pytest

from screens.account_interest_state import (
    build_interest_view_state,
    format_apr_micros,
    parse_apr_micros,
    parse_effective_date,
    next_available_effective_date,
)
from services.interest_services import (
    ExactInterestAmount,
    InterestEstimateSummary,
)


def summary(centavos):
    return InterestEstimateSummary(
        ExactInterestAmount(centavos, 0),
        centavos,
    )


def test_apr_parser_uses_exact_six_decimal_scaled_integer():
    assert parse_apr_micros("3.65") == 3_650_000
    assert parse_apr_micros("0.000001") == 1
    assert parse_apr_micros("0") == 0


@pytest.mark.parametrize(
    "value",
    ["", "abc", "-1", "1.0000001", "NaN", "Infinity"],
)
def test_apr_parser_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_apr_micros(value)


def test_apr_formatter_does_not_force_trailing_zeroes():
    assert format_apr_micros(3_650_000) == "3.65"
    assert format_apr_micros(1) == "0.000001"
    assert format_apr_micros(0) == "0"


def test_effective_date_requires_canonical_iso_date():
    assert parse_effective_date("2026-08-09") == "2026-08-09"
    with pytest.raises(ValueError):
        parse_effective_date("08/09/2026")


def test_enabled_view_state_has_textual_rate_and_estimates():
    profile = SimpleNamespace(
        annual_rate_micros=3_650_000,
        effective_from="2026-08-09",
    )

    state = build_interest_view_state(
        profile,
        summary(12),
        summary(345),
        "2026-08-09",
    )

    assert state.enabled is True
    assert state.apr_text == "3.65"
    assert state.day_count_text == "Actual/365"
    assert state.today_estimate_text == "₱ 0.12"
    assert state.accumulated_estimate_text == "₱ 3.45"
    assert state.summary_text == "Interest: 3.65% APR · accrued ₱ 3.45"


def test_disabled_view_state_is_explicit_and_defaults_date_to_today():
    state = build_interest_view_state(
        None,
        summary(0),
        summary(0),
        "2026-08-09",
    )

    assert state.enabled is False
    assert state.apr_text == ""
    assert state.effective_date_text == "2026-08-09"
    assert state.summary_text == "Interest: Off"


def test_next_available_effective_date_skips_existing_profile_dates():
    profiles = [
        SimpleNamespace(effective_from="2026-08-09"),
        SimpleNamespace(effective_from="2026-08-10"),
    ]

    assert next_available_effective_date(
        profiles,
        "2026-08-09",
    ) == "2026-08-11"
