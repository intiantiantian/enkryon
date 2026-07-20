from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_5_is_closed_and_phase_6_is_next():
    roadmap = read_project_file("ROADMAP.md")

    assert "Current position: Phase 5 is complete; Phase 6 is next" in roadmap
    assert (
        "| 5. Simpler, More Maintainable Code | "
        "Move business rules out of large screens and give each code layer "
        "one clear job. | Completed |"
    ) in roadmap
    assert "## Phase 5 — Simpler, More Maintainable Code" in roadmap
    assert "**Status:** Completed" in roadmap
    assert "Screens coordinate interface state" in roadmap
    assert "## Phase 6 — Clear, Accessible, Responsive" in roadmap
    assert "**Status:** Next" in roadmap


def test_phase_5_changes_are_recorded_for_users_and_developers():
    readme = read_project_file("README.md")
    changelog = read_project_file("CHANGELOG.md")
    architecture = read_project_file(
        "docs/development/architecture.md"
    )

    assert "Phase 5 simplified the architecture" in readme
    assert "Phase 6 is next" in readme
    assert "Named account, category-group, category" in changelog
    assert "Managed connections centralize" in architecture
    assert "Shared action-result rendering" in architecture


def test_phase_5_verification_records_closeout_evidence():
    verification = read_project_file(
        "docs/audits/phase-5-verification.md"
    )

    assert "Passed on July 20, 2026." in verification
    assert "`252` tests passed with coverage collection." in verification
    assert "Managed connections enable foreign keys" in verification
    assert "The current public release remains" in verification
    assert "GitHub Actions must pass" in verification


def test_phase_1_2_architecture_observation_is_resolved():
    summary = read_project_file(
        "docs/audits/phase-1-2-refactor-summary.md"
    )

    assert "Resolved in Phase 5 by extracting transaction form state" in summary
