from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = PROJECT_ROOT / "CHANGELOG.md"
RELEASE_GUIDE = PROJECT_ROOT / "docs" / "releases" / "README.md"
RELEASE_NOTES = (
    PROJECT_ROOT / "docs" / "releases" / "RELEASE_NOTES_TEMPLATE.md"
)
RELEASE_CHECKLIST = (
    PROJECT_ROOT
    / "docs"
    / "development"
    / "android-release-checklist.md"
)


def read_document(path):
    return path.read_text(encoding="utf-8")


def test_changelog_has_unreleased_and_current_release_sections():
    changelog = read_document(CHANGELOG)

    assert "## [Unreleased]" in changelog
    assert "## [0.4.0]" in changelog


def test_release_guide_defines_standard_artifact_names():
    guide = read_document(RELEASE_GUIDE)

    assert "Enkryon-vX.Y.Z.apk" in guide
    assert "Enkryon-vX.Y.Z.apk.sha256" in guide
    assert "Enkryon-vX.Y.Z-release-notes.md" in guide
    assert "sha256sum -c Enkryon-vX.Y.Z.apk.sha256" in guide
    assert "scripts/build-android-release.sh" in guide


def test_release_notes_template_records_upgrade_and_artifact_evidence():
    release_notes = read_document(RELEASE_NOTES)

    for required_heading in (
        "## User-visible changes",
        "## Upgrade and stored data",
        "## Android compatibility",
        "## Known limitations",
        "## Verification",
        "## Artifact",
    ):
        assert required_heading in release_notes

    assert "Official in-place upgrade" in release_notes
    assert "SHA-256" in release_notes


def test_release_checklist_covers_required_release_gates():
    checklist = read_document(RELEASE_CHECKLIST).lower()

    for required_gate in (
        "github actions",
        "legacy database fixture",
        "allowbackup",
        "apksigner",
        "zipalign",
        "clean installation",
        "official in-place upgrade",
        "adb install -r",
        "foreign_key_check",
        "force-stop and relaunch",
        "core workflow smoke test",
        "copied checksum",
    ):
        assert required_gate in checklist
