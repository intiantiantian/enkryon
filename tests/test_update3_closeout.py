from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_v1_3_release_candidate_identity_is_consistent():
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
    assert "Release status: `RELEASE CANDIDATE`" in release_notes
    assert "Enkryon-v1.3.0.apk" in release_notes


def test_v1_3_user_copy_describes_linked_account_effects():
    transfer_screen = read_project_file("screens/transfer.py")
    card = read_project_file("widgets/transaction_card.py")
    contract = read_project_file(
        "docs/development/pass-through-transfers.md"
    )
    normalized_contract = " ".join(contract.split())

    assert "FROM records the account outflow" in transfer_screen
    assert "TO records the account inflow" in transfer_screen
    assert "Cash is the outflow" in transfer_screen
    assert "Bank is the inflow" in transfer_screen
    assert "outflow | " in card
    assert " inflow" in card
    assert "same physical money" in normalized_contract


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
    assert "official v1.2.0 installation upgrades through migration 7" in checklist
    assert "Backup format 4 export" in checklist
    assert "Every transfer that exists before migration 7 becomes Internal" in normalized_release_notes


def test_v1_3_records_task_6_verified_evidence_without_claiming_android_release():
    verification = read_project_file(
        "docs/audits/update-3-pass-through-transfers-verification.md"
    )
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.3.0-release-notes.md"
    )

    assert "**90% verified**" in verification
    assert "`820 passed in 22.63s`" in verification
    assert "`01299eb`" in verification
    assert "Controlled format-4 export/Clear All Data/restore/relaunch: `PASSED`" in release_notes
    assert "GitHub Actions: `PENDING`" in release_notes
    assert "Official v1.2.0-to-v1.3.0 in-place upgrade: `PENDING`" in release_notes
