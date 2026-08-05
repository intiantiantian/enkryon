from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_v1_2_release_candidate_identity_is_consistent():
    main_source = read_project_file("main.py")
    readme = read_project_file("README.md")
    changelog = read_project_file("CHANGELOG.md")
    roadmap = read_project_file("ROADMAP.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.2.0-release-notes.md"
    )

    assert '__version__ = "1.2.0"' in main_source
    assert "Enkryon-v1.2.0.apk" in readme
    assert "## [1.2.0] - 2026-08-05" in changelog
    assert "Current release candidate: `v1.2.0`" in roadmap
    assert "# Enkryon v1.2.0" in release_notes
    assert "Enkryon-v1.2.0.apk" in release_notes


def test_v1_2_release_notes_describe_pending_financial_semantics():
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.2.0-release-notes.md"
    )
    normalized_release_notes = " ".join(release_notes.split())

    for phrase in (
        "does not affect account balances, Income, Expenses",
        "one atomic status transition",
        "Income and Expense filters now return posted records only",
        "backup format 3",
        "format-1 and format-2 documents",
    ):
        assert phrase in normalized_release_notes


def test_v1_2_release_notes_separate_pass_through_transfers():
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.2.0-release-notes.md"
    )
    roadmap = read_project_file("ROADMAP.md")

    assert "Pass-through cash-out activity is not part of this release" in release_notes
    assert "Pass-through Transfers (`v1.3.0`)" in roadmap


def test_v1_2_developer_docs_match_migration_and_architecture():
    database = read_project_file("docs/development/database.md")
    architecture = read_project_file("docs/development/architecture.md")

    assert "| 6 | `transaction_posting_status`" in database
    assert "transactions_posting_status_history_index" in database
    assert "Transaction posting status must be exactly `posted` or `temporary`" in database
    assert "Update 2 extends the architecture" in architecture
    assert "compare-and-set transition" in architecture
    assert "normalizing older formats" in architecture


def test_v1_2_android_checklist_requires_official_upgrade_and_recovery():
    checklist = read_project_file(
        "docs/development/android-release-checklist.md"
    )

    assert "A v1.1.0 installation upgrades through migration 6" in checklist
    assert "Every pre-upgrade transaction becomes posted" in checklist
    assert "one new Pending income" in checklist
    assert "Posting one Pending record after upgrade" in checklist
    assert "Backup format 3 export" in checklist


def test_v1_2_candidate_does_not_claim_unobserved_android_evidence():
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.2.0-release-notes.md"
    )

    for pending_evidence in (
        "GitHub Actions: `PENDING`",
        "Signature: `PENDING`",
        "Alignment: `PENDING`",
        "Official in-place upgrade: `PENDING`",
        "Size: `PENDING FINAL RELEASE BUILD`",
        "SHA-256: `PENDING FINAL RELEASE BUILD`",
    ):
        assert pending_evidence in release_notes
