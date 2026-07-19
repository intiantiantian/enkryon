from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_4_is_closed_and_phase_5_is_next():
    roadmap = read_project_file("ROADMAP.md")

    assert "Current release: `v0.4.8`" in roadmap
    assert "Current position: Phase 4 is complete; Phase 5 is next" in roadmap
    assert "**Status:** Completed in `v0.4.8`" in roadmap
    assert "**Passed.** Another developer can reproduce" in roadmap


def test_phase_4_release_is_recorded():
    changelog = read_project_file("CHANGELOG.md")
    verification = read_project_file("docs/audits/phase-4-verification.md")

    assert "## [0.4.8] - 2026-07-19" in changelog
    assert "Enkryon-v0.4.8.apk" in verification
    assert "45,767,240 bytes" in verification
    assert "adb install -r" in verification


def test_wsl_sync_preserves_generated_android_artifacts():
    android_build = read_project_file("docs/development/android-build.md")

    assert "--exclude='bin/'" in android_build
