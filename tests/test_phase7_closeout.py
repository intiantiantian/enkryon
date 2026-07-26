from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_7_remains_closed_after_phase_8():
    roadmap = read_project_file("ROADMAP.md")
    phase_seven = roadmap.split(
        "## Phase 7 — Backup, Restore, and Recovery",
        maxsplit=1,
    )[1].split(
        "## Phase 8 — Transaction Search and Advanced Filters",
        maxsplit=1,
    )[0]

    assert (
        "| 7. Backup, Restore, and Recovery | "
        "Let users preserve and recover their local financial records "
        "safely. | Completed |"
    ) in roadmap
    assert "**Status:** Completed in `v0.7.0`" in phase_seven
    assert "**Passed.**" in phase_seven


def test_phase_7_changes_are_recorded_for_users_and_developers():
    readme = read_project_file("README.md")
    changelog = read_project_file("CHANGELOG.md")
    architecture = read_project_file("docs/development/architecture.md")
    database = read_project_file("docs/development/database.md")
    testing = read_project_file("docs/development/testing.md")

    assert "Versioned, validated user-controlled backups" in readme
    assert (
        "Transactional replacement restore with rollback protection"
        in readme
    )
    assert "## [0.7.0] - 2026-07-25" in changelog
    assert "`services/backup_exporter.py`" in architecture
    assert "`services/backup_restorer.py`" in architecture
    assert "## User-Controlled Backup and Restore" in database
    assert "## Phase 7 Recovery Regression" in testing
    assert "`450` after documentation verification" in testing


def test_phase_7_verification_records_closeout_evidence():
    verification = read_project_file(
        "docs/audits/phase-7-verification.md"
    )

    assert "Passed on July 25, 2026." in verification
    assert (
        "`446` tests passed before the documentation closeout"
        in verification
    )
    assert (
        "`450` tests passed after the four Phase 7 closeout tests were added."
        in verification
    )
    assert "passed `10` focused document-transfer tests" in verification
    assert "broader `56`-test recovery and Settings regression" in verification
    assert (
        "d3656eb17ef11d1b333b63943326e16c3c8840ec3e13bd7814b0e0466c881ab4"
        in verification
    )
    assert "## Completion Gate" in verification


def test_phase_7_release_and_recovery_boundaries():
    database = read_project_file("docs/development/database.md")
    verification = read_project_file(
        "docs/audits/phase-7-verification.md"
    )

    assert "Restore in `v0.7.0` does not merge records" in database
    assert 'android:allowBackup="false"' in database
    assert "temporary debug verification build" in verification
    assert (
        "It is not the signed\n`v0.7.0` release artifact."
        in verification
    )
    assert "Backup merging is deferred until after statistics." in verification
    assert "Cloud synchronization remains outside Phase 7." in verification
    assert (
        "GitHub Actions and every artifact-specific release gate must pass"
        in verification
    )
