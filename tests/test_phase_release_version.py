from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_FILE = PROJECT_ROOT / "main.py"
README_FILE = PROJECT_ROOT / "README.md"
RELEASE_GUIDE = PROJECT_ROOT / "docs" / "releases" / "README.md"


def test_phase_8_release_uses_roadmap_version():
    main_source = MAIN_FILE.read_text(encoding="utf-8")
    readme = README_FILE.read_text(encoding="utf-8")
    release_guide = RELEASE_GUIDE.read_text(encoding="utf-8")
    normalized_guide = " ".join(release_guide.split())

    assert '__version__ = "0.8.0"' in main_source
    assert "Enkryon-v0.8.0.apk" in readme
    assert (
        "versions use `major.phase.subphase` as the roadmap reference"
        in normalized_guide
    )
    assert (
        "Phase 8 completion therefore prepares `v0.8.0` from "
        "`v0.7.0`."
        in normalized_guide
    )
