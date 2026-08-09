from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_v1_4_release_identity_is_consistent():
    main_source = read_project_file("main.py")
    readme = read_project_file("README.md")
    changelog = read_project_file("CHANGELOG.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.4.0-release-notes.md"
    )

    assert '__version__ = "1.4.0"' in main_source
    assert "Enkryon-v1.4.0.apk" in readme
    assert "## [1.4.0] - 2026-08-09" in changelog
    assert "# Enkryon v1.4.0" in release_notes
    assert "Release status: `RELEASED`" in release_notes


def test_v1_4_docs_lock_interest_financial_semantics():
    release_notes = " ".join(
        read_project_file(
            "docs/releases/Enkryon-v1.4.0-release-notes.md"
        ).split()
    )
    contract = " ".join(
        read_project_file(
            "docs/development/daily-bank-interest.md"
        ).split()
    )

    for phrase in (
        "nominal APR, not APY",
        "Actual/365",
        "prior end-of-day posted account balance",
        "Pending Transactions: excluded",
        "Pass-through Transfers: zero balance effect",
        "explicit reconciliation",
    ):
        assert phrase in release_notes

    assert "Sub-centavo value is never rounded away" in contract
    assert "ROUND_HALF_UP" in contract


def test_v1_4_schema_backup_and_architecture_are_documented():
    database = read_project_file("docs/development/database.md")
    architecture = read_project_file("docs/development/architecture.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.4.0-release-notes.md"
    )

    assert "| 10 | `daily_bank_interest`" in database
    assert "Backup format 5 is the active Update 4 format" in database
    assert "Update 4 keeps estimated interest outside" in architecture
    assert "formats 1 through 4 remain restorable" in release_notes.lower()


def test_v1_4_android_checklist_requires_official_upgrade_and_recovery():
    checklist = read_project_file(
        "docs/development/android-release-checklist.md"
    )

    assert "Current v1.4.0 upgrade additions" in checklist
    assert "official v1.3.0 installation upgrades through migration 10" in checklist
    assert "Backup format 5 export" in checklist
    assert "Remove Interest clears interest-only tracking" in checklist


def test_v1_4_verification_records_observed_release_evidence():
    verification = read_project_file(
        "docs/audits/update-4-daily-bank-interest-verification.md"
    )
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.4.0-release-notes.md"
    )

    assert "918 passed in 31.14s" in verification
    assert "82%" in verification
    assert "fe34913" in verification
    assert "45,802,212" in verification
    assert "102410400" in verification
    assert "7f58a722423eb736772534dc83832061e779a52578ec1471e7471084a2ab45e9" in verification
    assert "GitHub Actions: passed" in verification
    assert "in-place upgrade with `adb install -r`: passed" in verification
    assert "PENDING FINAL" not in release_notes
    assert "Release status: `RELEASED`" in release_notes
    assert "Release status: `VERIFIED RELEASE CANDIDATE`" not in release_notes
