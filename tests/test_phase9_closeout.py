from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_version_1_source_terms_reserve_copy_and_reuse_rights():
    license_text = read_project_file("LICENSE")
    readme = read_project_file("README.md")

    assert "Copyright (c) 2026 Christian Jay Villaria" in license_text
    assert "All rights reserved." in license_text
    for restricted_action in (
        "copy",
        "modify",
        "distribute",
        "reuse",
    ):
        assert restricted_action in readme
    assert "See [LICENSE](LICENSE)" in readme


def test_version_1_release_identity_remains_recorded():
    changelog = read_project_file("CHANGELOG.md")
    roadmap = read_project_file("ROADMAP.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.0.0-release-notes.md"
    )

    assert "## [1.0.0] - 2026-07-28" in changelog
    assert "**Status:** Completed in `v1.0.0`" in roadmap
    assert "# Enkryon v1.0.0" in release_notes
    assert "Enkryon-v1.0.0.apk" in release_notes


def test_roadmap_points_to_the_remaining_release_gate():
    roadmap = read_project_file("ROADMAP.md")

    assert roadmap.count("## Current Project Snapshot") == 1
    assert (
        "| 9. Beta Testing and Version 1.0 Readiness | "
        "Prove that the complete core app is stable enough for a version "
        "1.0 release. | Completed |"
    ) in roadmap
    assert "**Status:** Completed in `v1.0.0`" in roadmap
    assert "Define search behavior for notes" not in roadmap


def test_version_1_developer_documents_match_verified_architecture():
    architecture = read_project_file("docs/development/architecture.md")
    database = read_project_file("docs/development/database.md")
    testing = read_project_file("docs/development/testing.md")
    verification = read_project_file(
        "docs/audits/phase-9-verification.md"
    )

    assert "`RecycleView` data" in architecture
    assert "Phase 9 verified the same boundaries with 10,000" in architecture
    assert "## Large-History Access" in database
    assert "Restore in `v1.0.0` does not merge records" in database
    assert "## Phase 9 Release-Readiness Regression" in testing
    assert "## Version 1.0 Release-Candidate Preparation" in verification
