from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_v1_3_release_identity_is_consistent():
    main_source = read_project_file("main.py")
    readme = read_project_file("README.md")
    changelog = read_project_file("CHANGELOG.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.3.0-release-notes.md"
    )

    assert '__version__ = "1.3.0"' in main_source
    assert "Enkryon-v1.3.0.apk" in readme
    assert "## [1.3.0] - 2026-08-07" in changelog
    assert "# Enkryon v1.3.0" in release_notes
    assert "Release status: `BALANCE-NEUTRALITY CORRECTION CANDIDATE`" in release_notes
    assert "Enkryon-v1.3.0.apk" in release_notes


def test_v1_3_user_copy_describes_balance_neutral_exchange():
    transfer_screen = read_project_file("screens/transfer.py")
    card = read_project_file("widgets/transaction_card.py")
    transfer_kv = read_project_file("kv/transfer.kv")
    contract = read_project_file(
        "docs/development/pass-through-transfers.md"
    )
    normalized_contract = " ".join(contract.split())

    assert "neither account balance changes" in transfer_screen
    assert "PAID FROM" in transfer_kv
    assert "RECEIVED INTO" in transfer_kv
    assert "paid from | " in card
    assert " received into" in card
    assert "source account balance change = 0" in normalized_contract
    assert "destination account balance change = 0" in normalized_contract

def test_v1_3_release_docs_lock_migration_backup_and_upgrade_gate():
    database = read_project_file("docs/development/database.md")
    checklist = read_project_file(
        "docs/development/android-release-checklist.md"
    )
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.3.0-release-notes.md"
    )
    normalized_release_notes = " ".join(release_notes.split())

    assert "| 7 | `account_transfer_kinds`" in database
    assert "backup format 4" in database
    assert "official v1.2.0 installation upgrades through migrations 7, 8, and 9" in checklist
    assert "Backup format 4 export" in checklist
    assert "Every transfer that exists before migration 7 becomes Internal" in normalized_release_notes


def test_v1_3_records_accounting_correction_gate():
    verification = read_project_file(
        "docs/audits/update-3-pass-through-transfers-verification.md"
    )
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.3.0-release-notes.md"
    )
    normalized_notes = " ".join(release_notes.split())

    assert "Release blocked pending corrected build" in verification
    assert "## Accounting Correction" in verification
    assert "Release status: `BALANCE-NEUTRALITY CORRECTION CANDIDATE`" in release_notes
    assert "Publication remains stopped before merge/tag" in normalized_notes
    assert "zero balance effect" in normalized_notes
    assert "Neither participating account balance" in normalized_notes
