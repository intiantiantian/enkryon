from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_6_is_closed_and_phase_7_is_next():
    roadmap = read_project_file("ROADMAP.md")
    phase_six = roadmap.split(
        "## Phase 6 — Clear, Accessible, Responsive User Experience",
        maxsplit=1,
    )[1].split(
        "## Phase 7 — Backup, Restore, and Recovery",
        maxsplit=1,
    )[0]

    assert "Updated: July 23, 2026" in roadmap
    assert "Current release: `v0.6.0`" in roadmap
    assert "Current position: Phase 6 is complete; Phase 7 is next" in roadmap
    assert (
        "| 6. Clear, Accessible, Responsive User Experience | "
        "Make all existing workflows comfortable and understandable across "
        "supported phones. | Completed |"
    ) in roadmap
    assert (
        "| 7. Backup, Restore, and Recovery | "
        "Let users preserve and recover their local financial records "
        "safely. | Next |"
    ) in roadmap
    assert "**Status:** Completed" in phase_six
    assert "**Passed.**" in phase_six


def test_phase_6_changes_are_recorded_for_users_and_developers():
    readme = read_project_file("README.md")
    changelog = read_project_file("CHANGELOG.md")
    testing = read_project_file("docs/development/testing.md")

    assert "Phase 6 improved existing workflows" in readme
    assert (
        "Reusable card-based selection, input, and confirmation overlays"
        in changelog
    )
    assert "## Phase 6 Interface Regression" in testing
    assert "`395` passing tests" in testing
    assert "Small `S / 90%` profile" in testing
    assert "Enkryon-v0.6.0.apk" in readme
    assert "## [0.6.0] - 2026-07-23" in changelog


def test_phase_6_verification_records_closeout_evidence():
    verification = read_project_file(
        "docs/audits/phase-6-verification.md"
    )

    assert "Passed on July 23, 2026." in verification
    assert "`391` tests passed before the documentation closeout." in verification
    assert (
        "`395` tests passed after the four Phase 6 closeout tests were added."
        in verification
    )
    assert (
        "The exhaustive final all-profile manual checklist was not repeated"
        in verification
    )
    assert (
        "The narrow income and expense summary cards may shorten"
        in verification
    )


def test_phase_6_release_and_recovery_boundaries():
    roadmap = read_project_file("ROADMAP.md")
    verification = read_project_file(
        "docs/audits/phase-6-verification.md"
    )

    assert "Current release: `v0.6.0`" in roadmap
    assert "Phase 6's source release is `v0.6.0`." in verification
    assert "Artifact-specific Android build" in verification
    assert "Repository screenshot replacement" in verification
    assert "Android backup remains disabled until Phase 7" in verification
