from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = PROJECT_ROOT / "docs" / "development" / "daily-bank-interest.md"
ROADMAP = PROJECT_ROOT / "ROADMAP.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_update4_daily_interest_contract_locks_rate_and_day_basis():
    contract = read(CONTRACT)

    assert "nominal annual percentage rate (**APR**), not APY" in contract
    assert "annual_rate_micros" in contract
    assert "`3.65%` is stored as `3_650_000`" in contract
    assert "Actual/365" in contract
    assert "including February 29" in contract
    assert "denominator of 365" in contract


def test_update4_contract_uses_prior_posted_closing_balance():
    contract = read(CONTRACT)

    assert "end of calendar date `D - 1`" in contract
    assert "Pending Transactions are excluded" in contract
    assert "Internal Transfers affect each participating account directionally" in contract
    assert "Pass-through Transfers contribute zero" in contract
    assert "Zero or negative closing balances accrue zero positive interest" in contract


def test_update4_contract_preserves_exact_subcentavo_value():
    contract = read(CONTRACT)

    assert "36_500_000_000" in contract
    assert "divmod" in contract
    assert "exact rational remainder" in contract
    assert "Sub-centavo value is never rounded away" in contract
    assert "ROUND_HALF_UP" in contract
    assert "rounded once from the exact accumulated value" in " ".join(contract.split())


def test_update4_contract_locks_rate_history_idempotency_and_reconciliation():
    contract = read(CONTRACT)

    assert "Rate changes are effective-dated" in contract
    assert "snapshots the rate used" in contract
    assert "deterministic and idempotent" in contract
    assert "exactly one normal posted Income transaction" in contract
    assert "cannot produce duplicate Income" in contract
    assert "variance" in contract


def test_update4_contract_reserves_next_schema_and_backup_versions():
    contract = read(CONTRACT)
    roadmap = read(ROADMAP)

    assert "migration **10**" in contract
    assert "backup format **5**" in contract
    assert "Daily Bank Interest (`v1.4.0`)" in roadmap
