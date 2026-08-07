from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_update_3_contract_locks_cash_to_bank_direction_and_financial_rules():
    contract = read_project_file("docs/development/pass-through-transfers.md")
    normalized_contract = " ".join(contract.split())

    assert "Cash → Bank" in contract
    assert "The source is always the user-owned account whose balance decreases" in normalized_contract
    for invariant in (
        "all-account balance change = 0",
        "Income change = 0",
        "Expenses change = 0",
        "category-total change = 0",
        "posted net-cash-flow change = 0",
    ):
        assert invariant in contract
    assert "All stored and calculated money remains integer centavos" in normalized_contract


def test_update_3_contract_locks_transfer_kind_and_compatibility_direction():
    contract = read_project_file("docs/development/pass-through-transfers.md")
    normalized_contract = " ".join(contract.split())

    assert "extend the existing `account_transfers` ledger" in normalized_contract
    assert "`internal` means the ordinary first-class Account Transfer" in normalized_contract
    assert "`pass_through` means the completed cash-out" in normalized_contract
    assert "Every transfer that exists before migration 7 becomes `internal`" in normalized_contract
    assert "migrations 1 through 6 must remain unchanged" in normalized_contract
    assert "Backup format 4 preserves `transfer_kind`" in normalized_contract
    assert "formats 1 through 3" in normalized_contract
    assert "normalize to `internal`" in normalized_contract


def test_update_3_contract_locks_counterparty_fee_and_scope_rules():
    contract = read_project_file("docs/development/pass-through-transfers.md")
    normalized_contract = " ".join(contract.split())

    assert "optional `counterparty` text field" in normalized_contract
    assert "Notes field carries any optional purpose" in normalized_contract
    assert "service charge or fee is not part of the Pass-through principal" in normalized_contract
    assert "separately as a normal posted Expense" in normalized_contract
    assert "Partial settlement, multiple counterparties, debts, loans, receivables" in normalized_contract
    assert "multi-leg exchanges are outside v1.3.0" in normalized_contract


def test_update_3_contract_locks_activity_search_and_filter_semantics():
    contract = read_project_file("docs/development/pass-through-transfers.md")
    normalized_contract = " ".join(contract.split())

    assert "visible `Pass-through` text" in contract
    assert "primary `Transfer` filter includes both `internal` and `pass_through`" in normalized_contract
    assert "distinguish `Internal` from `Pass-through`" in normalized_contract
    assert "`Income` and `Expense` filters exclude all transfers" in normalized_contract
    assert "`Pending` includes only Pending income/expense transactions" in normalized_contract
    assert "Search for Pass-through activity includes counterparty" in normalized_contract
    assert "Stable newest-first ordering remains `date_time DESC, id DESC`" in normalized_contract


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
