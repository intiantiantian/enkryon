from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_update_2_contract_locks_non_posting_financial_semantics():
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )

    assert "A pending transaction is fully non-posting" in contract
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

    assert "visible `Pending` text label" in contract
    assert "The `Pending` activity filter returns only pending income and expense" in contract
    assert "`Income` and `Expense` activity filters return posted records only" in contract
    assert "An account referenced by a posted or pending transaction cannot be deleted" in contract
    assert "category group referenced by a posted or pending transaction" in contract


def test_update_2_contract_locks_migration_and_backup_compatibility():
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    roadmap = read_project_file("ROADMAP.md")

    assert "Migration 6 extends the existing `transactions` table" in contract
    assert "migrations 1 through 5 are released history" in contract
    assert "Backup format 3 preserves each transaction's posting status" in contract
    assert "Format-1 and format-2 transactions normalize to `posted`" in contract
    assert "Pending Transactions (`v1.2.0`)" in roadmap
    assert "Pass-through Transfers (`v1.3.0`)" in roadmap
    assert "Daily Bank Interest (`v1.4.0`)" in roadmap
    assert "Statistical Visualizations (`v1.5.0`)" in roadmap
    assert "`temporary` remains the internal database and code value" in contract
    assert "user-facing product term is **Pending**" in contract


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

    assert "| 3. Add form state and service workflows | 18% | Verified |" in verification
    assert "Task 3 gate" in verification
    assert "Task 3A" in verification
    assert "Task 3B" in verification
    assert "`61` tests" in normalized_verification
    assert "`89` tests" in normalized_verification
    assert "`666 passed`" in verification
    assert "`682 passed`" in verification
    assert "ordinary save path" in verification
    assert "pending save/edit workflow gate" in testing
    assert "posting and recovery workflow gate" in testing
    assert (
        "Ordinary save and edit workflows cannot change posting status"
        in contract
    )
    assert "UI-independent save, edit, atomic" in roadmap
    assert "compare-and-set status update" in contract
    assert "Delete and undo-restore preserve" in contract



def test_update_2_task_4a_records_explicit_form_actions():
    verification = read_project_file(
        "docs/audits/update-2-temporary-transactions-verification.md"
    )
    testing = read_project_file("docs/development/testing.md")
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    roadmap = read_project_file("ROADMAP.md")
    layout = read_project_file("kv/add_transaction.kv")
    screen = read_project_file("screens/add_transaction.py")
    normalized_verification = " ".join(verification.split())

    assert "Task 4A raised verified progress to `54%`." in (
        normalized_verification
    )
    assert "Task 4A Form Actions Evidence" in verification
    assert "`82` tests" in verification
    assert "`696 passed`" in verification
    assert "transaction-form interface gate" in testing
    assert "Save as Pending" in contract
    assert "Post Transaction" in contract
    assert "Already Posted" in contract
    assert "explicit pending form actions" in roadmap
    assert "id: posting_status_label" in layout
    assert "id: temporary_action" in layout
    assert "id: post_action" in layout
    assert "icon: 'content-save'" not in layout
    assert "save_temporary_transaction" in screen
    assert "post_transaction_workflow" in screen


def test_update_2_task_4b_records_activity_status_and_direct_posting():
    verification = read_project_file(
        "docs/audits/update-2-temporary-transactions-verification.md"
    )
    testing = read_project_file("docs/development/testing.md")
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    roadmap = read_project_file("ROADMAP.md")
    card_layout = read_project_file("kv/widgets.kv")
    card_source = read_project_file("widgets/transaction_card.py")
    actions_source = read_project_file(
        "screens/transaction_list_actions.py"
    )
    normalized_roadmap = " ".join(roadmap.split())

    assert "Task 4B raised verified progress to `63%`." in verification
    assert (
        "| 4. Build pending transaction interface | 20% | Verified |"
        in verification
    )
    assert "Task 4B Activity Interface Evidence" in verification
    assert "`707 passed`" in verification
    assert "activity-card interface gate" in testing
    assert "Unified Activity records carry posting status" in contract
    assert "guarded post action" in contract
    assert "Completed: add explicit pending form actions" in roadmap
    assert "id: posting_status_badge" in card_layout
    assert "id: post_transaction_action" in card_layout
    assert "posting_status_label" in card_source
    assert "confirm_post_transaction" in card_source
    assert "Post Pending Transaction?" in actions_source
    assert "refresh_after_transaction_post" in actions_source


def test_update_2_task_5_records_pending_filter_and_financial_integration():
    verification = read_project_file(
        "docs/audits/update-2-temporary-transactions-verification.md"
    )
    testing = read_project_file("docs/development/testing.md")
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    roadmap = read_project_file("ROADMAP.md")
    activity_repository = read_project_file(
        "database/activity_repository.py"
    )
    dashboard_layout = read_project_file("kv/dashboard.kv")
    history_layout = read_project_file("kv/transactions.kv")

    assert "Task 5 Activity and Financial Integration Evidence" in verification
    assert (
        "| 5. Integrate balances, totals, and activity filters | 16% | Verified |"
        in verification
    )
    assert "Task 5 Activity and Financial Integration Evidence" in verification
    assert "`725 passed`" in verification
    assert "Task 5 activity and financial integration gate" in testing
    assert "The `All` activity filter combines" in contract
    assert "Existing `Income` and `Expense` activity filters return posted records only" in contract
    normalized_contract = " ".join(contract.split())
    assert (
        "Pending activity regression confirms that the shared Activity query "
        "also uses this index"
        in normalized_contract
    )
    assert "Completed: add posted-only Income and Expense filters" in roadmap
    assert "posting_status" in activity_repository
    assert "transactions.posting_status = 'posted'" in activity_repository
    for layout in (dashboard_layout, history_layout):
        assert "id: pending_filter" in layout
        assert "text: 'PENDING'" in layout
        assert "root.set_transaction_filter('pending')" in layout

def test_update_2_task_6_records_backup_format_3_recovery_evidence():
    verification = read_project_file(
        "docs/audits/update-2-temporary-transactions-verification.md"
    )
    testing = read_project_file("docs/development/testing.md")
    contract = read_project_file(
        "docs/development/temporary-transactions.md"
    )
    roadmap = read_project_file("ROADMAP.md")
    backup_format = read_project_file("services/backup_format.py")
    backup_validator = read_project_file(
        "services/backup_validator.py"
    )

    assert "Verified weighted progress: `90%`." in verification
    assert (
        "| 6. Extend backup and recovery | 11% | Verified |"
        in verification
    )
    assert "Task 6 Backup and Recovery Evidence" in verification
    assert "`737 passed`" in verification
    assert "Task 6 backup and recovery gate" in testing
    assert "Format-1 and format-2 transactions normalize to `posted`" in (
        contract
    )
    assert "completed Task 6 backup and" in roadmap
    assert "TRANSFER_BACKUP_FORMAT_VERSION = 2" in backup_format
    assert "BACKUP_FORMAT_VERSION = 3" in backup_format
    assert '"posting_status"' in backup_format
    assert 'transaction["posting_status"] = "posted"' in (
        backup_validator
    )
