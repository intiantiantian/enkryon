from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_update_1_release_candidate_identity_is_consistent():
    changelog = read_project_file("CHANGELOG.md")
    roadmap = read_project_file("ROADMAP.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.1.0-release-notes.md"
    )

    assert "## [1.1.0] - 2026-08-04" in changelog
    assert "### Update 1 — Account Transfers (`v1.1.0`)" in roadmap
    assert "# Enkryon v1.1.0" in release_notes
    assert "Enkryon-v1.1.0.apk" in release_notes


def test_update_1_documents_transfer_financial_invariants():
    readme = read_project_file("README.md")
    transfer_contract = read_project_file(
        "docs/development/account-transfers.md"
    )
    database = read_project_file("docs/development/database.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.1.0-release-notes.md"
    )

    for document in (transfer_contract, database, release_notes):
        assert "integer centavos" in document or "integer-centavo" in document

    assert "Keep Internal and Pass-through principal out of Income and Expenses" in readme
    assert "all-accounts transfer contribution" in database
    assert "all-accounts balance, Income, Expenses" in release_notes


def test_update_1_documents_migration_and_backup_compatibility():
    database = read_project_file("docs/development/database.md")
    testing = read_project_file("docs/development/testing.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.1.0-release-notes.md"
    )

    assert "| 5 | `account_transfers`" in database
    assert "backup format 2" in database
    assert "format-1 documents from version 1.0" in database
    assert "## Update 1 Account-Transfer Regression" in testing
    assert "Compatible format-1" in release_notes


def test_update_1_verification_records_release_exception():
    verification = read_project_file(
        "docs/audits/update-1-account-transfers-verification.md"
    )
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.1.0-release-notes.md"
    )
    assert "Verified weighted progress: `90%`." in verification
    assert "Accepted Release Exception" in verification
    assert "waived by the release owner" in verification
    assert "637 PASSED; 83% TOTAL COVERAGE" in release_notes
    assert "SKIPPED BY RELEASE OWNER" in release_notes
    assert "45,763,428 bytes" in release_notes
    assert (
        "3fa66d0e5804fd8bbb5b9707157f951d"
        "d062ef06d2f3f9377e4ed31c2c4db79a"
        in release_notes
    )
    assert "PENDING FINAL RELEASE BUILD" not in release_notes
    assert "official Android `v1.0.0` to `v1.1.0`" in release_notes
