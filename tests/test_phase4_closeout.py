from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_4_remains_closed_after_phase_6():
    roadmap = read_project_file("ROADMAP.md")
    phase_four = roadmap.split(
        "## Phase 4 — Reliable Android Releases",
        maxsplit=1,
    )[1].split(
        "## Phase 5 — Simpler, More Maintainable Code",
        maxsplit=1,
    )[0]

    assert "**Status:** Completed in `v0.4.8`" in phase_four
    assert "**Passed.** Another developer can reproduce" in phase_four


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
