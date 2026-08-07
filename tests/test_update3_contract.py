from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_update_3_contract_locks_balance_neutral_accounting():
    contract = read_project_file("docs/development/pass-through-transfers.md")
    normalized = " ".join(contract.split())

    assert "one complete counterparty exchange" in normalized
    assert "zero balance effect on every participating user account" in normalized
    for invariant in (
        "Pass-through source account balance change = 0",
        "Pass-through destination account balance change = 0",
        "Pass-through all-account balance change = 0",
        "Income change = 0",
        "Expenses change = 0",
        "category-total change = 0",
        "posted net-cash-flow change = 0",
    ):
        assert invariant in contract
    assert "must never change either participating account balance" in normalized
    assert "All stored money remains integer centavos" in normalized

def test_update_3_contract_locks_transfer_kind_and_compatibility_direction():
    contract = read_project_file("docs/development/pass-through-transfers.md")
    normalized = " ".join(contract.split())

    assert "`internal` means the ordinary first-class Account Transfer" in normalized
    assert "`pass_through` identifies the cash-out/money-forwarding parent" in normalized
    assert "Every transfer that exists before migration 7 becomes `internal`" in normalized
    assert "Migration 8 is superseded development history" in normalized
    assert "Migration 9 removes those temporary movement artifacts" in normalized
    assert "Backup format 4 preserves `transfer_kind`" in normalized
    assert "Formats 1 through 3 remain supported" in normalized
    assert "normalize older transfers to `internal`" in normalized


def test_update_3_contract_locks_counterparty_fee_and_scope_rules():
    contract = read_project_file("docs/development/pass-through-transfers.md")
    normalized = " ".join(contract.split())

    assert "optional counterparty" in normalized
    assert "service charge or fee is recorded separately" in normalized
    assert "Partial settlement" in normalized
    assert "loans" in normalized
    assert "multi-leg exchanges" in normalized


def test_update_3_contract_locks_activity_search_and_filter_semantics():
    contract = read_project_file("docs/development/pass-through-transfers.md")
    normalized = " ".join(contract.split())

    assert "primary Transfer filter includes Internal and Pass-through" in normalized
    assert "Advanced filters distinguish the two kinds" in normalized
    assert "Income, Expense, and Pending meanings remain unchanged" in normalized
    assert "Search includes counterparty" in normalized
    assert "Stable newest-first ordering remains `date_time DESC, id DESC`" in normalized


def test_update_3_task_1_records_baseline_and_weighted_plan():
    verification = read_project_file(
        "docs/audits/update-3-pass-through-transfers-verification.md"
    )
    testing = read_project_file("docs/development/testing.md")

    assert "`746 passed in 32.69s`" in verification
    assert "Recorded total branch coverage: `83%`" in verification
    assert "Task 1 changes documentation and contract tests only" in verification
    assert "Task 1 changes documentation and contract tests only" in testing

    weights = (9, 18, 17, 18, 16, 12, 10)
    assert sum(weights) == 100
    for weight in weights:
        assert f"| {weight}% |" in verification


def test_update_3_task_6_locks_backup_format_4_compatibility():
    backup_format = read_project_file("services/backup_format.py")
    backup_validator = read_project_file("services/backup_validator.py")
    testing = read_project_file("docs/development/testing.md")
    verification = read_project_file(
        "docs/audits/update-3-pass-through-transfers-verification.md"
    )

    assert "POSTING_STATUS_BACKUP_FORMAT_VERSION = 3" in backup_format
    assert "PASS_THROUGH_BACKUP_FORMAT_VERSION = 4" in backup_format
    assert '"transfer_kind"' in backup_format
    assert '"counterparty"' in backup_format
    assert 'transfer["transfer_kind"] = "internal"' in backup_validator
    assert 'transfer["counterparty"] = None' in backup_validator
    assert "10,000-transfer mixed-history round trip" in testing
    assert "formats 1 through 4" in verification
