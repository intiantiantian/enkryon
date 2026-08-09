from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_FILE = PROJECT_ROOT / "main.py"
README_FILE = PROJECT_ROOT / "README.md"
RELEASE_GUIDE = PROJECT_ROOT / "docs" / "releases" / "README.md"


def test_current_release_candidate_uses_version_1_3_identity():
    main_source = MAIN_FILE.read_text(encoding="utf-8")
    readme = README_FILE.read_text(encoding="utf-8")
    release_guide = RELEASE_GUIDE.read_text(encoding="utf-8")
    normalized_guide = " ".join(release_guide.split())

    assert '__version__ = "1.3.0"' in main_source
    assert "Enkryon-v1.3.0.apk" in readme
    assert (
        "versions used `major.phase.subphase` as the roadmap reference"
        in normalized_guide
    )
    assert (
        "Phase 9 prepares the first stable release, `v1.0.0`, from "
        "official `v0.8.0`."
        in normalized_guide
    )
    assert (
        "Update 1 prepares `v1.1.0` from official `v1.0.0`"
        in normalized_guide
    )
    assert (
        "Update 2 prepares `v1.2.0` from official `v1.1.0`"
        in normalized_guide
    )
    assert (
        "Update 3 releases `v1.3.0` from official `v1.2.0`"
        in normalized_guide
    )
