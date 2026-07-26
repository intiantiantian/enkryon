from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_8_is_closed_and_phase_9_is_next():
    roadmap = read_project_file("ROADMAP.md")
    phase_eight = roadmap.split(
        "## Phase 8 — Transaction Search and Advanced Filters",
        maxsplit=1,
    )[1].split(
        "## Phase 9 — Beta Testing and Version 1.0 Readiness",
        maxsplit=1,
    )[0]
    phase_nine = roadmap.split(
        "## Phase 9 — Beta Testing and Version 1.0 Readiness",
        maxsplit=1,
    )[1]

    assert "Updated: July 26, 2026" in roadmap
    assert "Current release: `v0.8.0`" in roadmap
    assert "Current position: Phase 8 is complete; Phase 9 is next" in roadmap
    assert (
        "| 8. Transaction Search and Advanced Filters | "
        "Help users find specific transactions quickly, even in large "
        "histories. | Completed |"
    ) in roadmap
    assert (
        "| 9. Beta Testing and Version 1.0 Readiness | "
        "Prove that the complete core app is stable enough for a version "
        "1.0 release. | Next |"
    ) in roadmap
    assert "**Status:** Completed in `v0.8.0`" in phase_eight
    assert "**Passed.**" in phase_eight
    assert "**Status:** Next" in phase_nine


def test_phase_8_changes_are_recorded_for_users_and_developers():
    readme = read_project_file("README.md")
    changelog = read_project_file("CHANGELOG.md")
    testing = read_project_file("docs/development/testing.md")
    release_guide = read_project_file("docs/releases/README.md")

    assert "Combined transaction search and advanced filters" in readme
    assert "Indexed newest-first transaction history" in readme
    assert "## [0.8.0] - 2026-07-26" in changelog
    assert "## Phase 8 Search and Filter Regression" in testing
    assert "`499` after documentation verification" in testing
    assert (
        "Phase 8 completion therefore prepares `v0.8.0` from "
        "`v0.7.0`."
        in " ".join(release_guide.split())
    )


def test_phase_8_verification_records_closeout_evidence():
    verification = read_project_file(
        "docs/audits/phase-8-verification.md"
    )

    assert "Passed on July 26, 2026." in verification
    assert (
        "`495` tests passed before the documentation closeout"
        in verification
    )
    assert (
        "`499` tests passed after the four Phase 8 closeout tests were added."
        in verification
    )
    assert "`81%` total" in verification
    assert "10,000-record history" in verification
    assert "## Completion Gate" in verification


def test_phase_8_performance_and_release_boundaries():
    verification = read_project_file(
        "docs/audits/phase-8-verification.md"
    )

    assert "does not use an elapsed-time threshold" in verification
    assert "database version 3 backups remain restorable" in verification
    assert "signed Android `v0.8.0` release artifact remains pending" in (
        verification
    )
    assert (
        "Phase 9 will perform broader device, upgrade, accessibility, and beta"
        in verification
    )
