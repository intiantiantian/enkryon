from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_update_2_contract_locks_non_posting_financial_semantics():
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )

    assert "A temporary transaction is fully non-posting" in contract
    for excluded_result in (
        "selected account balance",
        "total Income or Expenses",
        "category or category-group totals",
        "net cash flow",
        "statistical financial aggregates",
    ):
        assert excluded_result in contract
    assert "All stored and calculated money remains integer centavos" in contract


def test_update_2_contract_locks_status_and_atomic_posting_rules():
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    normalized_contract = " ".join(contract.split())

    assert "`posted` means the transaction is financially effective" in contract
    assert "`temporary` means the transaction is planned" in contract
    assert "Every transaction that exists before migration 6 becomes `posted`" in contract
    assert "Posting converts the existing record" in contract
    assert "one atomic database operation" in normalized_contract
    assert "A repeated attempt to post an already-posted transaction" in contract
    assert "does not auto-post, auto-expire" in contract


def test_update_2_contract_locks_activity_and_relationship_behavior():
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )

    assert "visible `Temporary` text label" in contract
    assert "The `Temporary` activity filter returns temporary income and expense" in contract
    assert "`Income` and `Expense` activity filters return posted records only" in contract
    assert "An account referenced by a posted or temporary transaction cannot be deleted" in contract
    assert "category group referenced by a posted or temporary transaction" in contract


def test_update_2_contract_locks_migration_and_backup_compatibility():
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    roadmap = read_project_file("ROADMAP.md")

    assert "Migration 6 extends the existing `transactions` table" in contract
    assert "migrations 1 through 5 are released history" in contract
    assert "Backup format 3 preserves each transaction's posting status" in contract
    assert "Format-1 and format-2 transactions restore as `posted`" in contract
    assert "Temporary Transactions (`v1.2.0`)" in roadmap
    assert "Daily Bank Interest (`v1.3.0`)" in roadmap
    assert "Statistical Visualizations (`v1.4.0`)" in roadmap


def test_update_2_task_1_records_baseline_progress_and_release_exception():
    verification = read_project_file(
        "docs/audits/update-2-temporary-transactions-verification.md"
    )
    testing = read_project_file("docs/development/testing.md")
    roadmap = read_project_file("ROADMAP.md")
    normalized_verification = " ".join(verification.split())

    assert (
        "| 1. Lock status semantics and baseline | 7% | Verified |"
        in verification
    )
    assert "`637 passed in 16.45s`" in verification
    assert "Recorded total branch coverage: `83%`" in verification
    assert "Task 1 changes documentation and contract tests only" in testing
    assert "release-owner waiver" in normalized_verification
    assert (
        "`v1.1.0`-to-`v1.2.0` official in-place upgrade"
        in normalized_verification
    )
    assert "explicit carried exception" in roadmap


def test_update_2_task_2_records_status_aware_persistence_evidence():
    verification = read_project_file(
        "docs/audits/update-2-temporary-transactions-verification.md"
    )
    testing = read_project_file("docs/development/testing.md")
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    roadmap = read_project_file("ROADMAP.md")
    normalized_testing = " ".join(testing.split())
    normalized_contract = " ".join(contract.split())

    assert "| 2. Add migration and status-aware persistence | 18% | Verified |" in verification
    assert "Task 2 was completed in two checkpoints" in verification
    assert "`653 passed`" in verification
    assert "`654 passed`" in verification
    assert "transactions_posting_status_history_index" in verification
    assert "10,000-record history regression" in testing
    assert "temporary B-tree" in normalized_testing
    assert (
        "Account- or category-specific status indexes remain deferred"
        in normalized_contract
    )
    assert "Completed: add migration 6" in roadmap


def test_update_2_task_3_records_complete_service_workflows():
    verification = read_project_file(
        "docs/audits/update-2-temporary-transactions-verification.md"
    )
    testing = read_project_file("docs/development/testing.md")
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    roadmap = read_project_file("ROADMAP.md")
    normalized_verification = " ".join(verification.split())

    assert "Verified weighted progress: `43%`." in verification
    assert "Task 3 complete" in verification
    assert "Task 3A" in verification
    assert "Task 3B" in verification
    assert "`61` tests" in normalized_verification
    assert "`89` tests" in normalized_verification
    assert "`666 passed`" in verification
    assert "`682 passed`" in verification
    assert "ordinary save path" in verification
    assert "temporary save/edit workflow gate" in testing
    assert "posting and recovery workflow gate" in testing
    assert (
        "Ordinary save and edit workflows cannot change posting status"
        in contract
    )
    assert "UI-independent save, edit, atomic" in roadmap
    assert "compare-and-set status update" in contract
    assert "Delete and undo-restore preserve" in contract
