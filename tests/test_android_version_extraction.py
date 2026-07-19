from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_SCRIPT = PROJECT_ROOT / "scripts" / "build-android-release.sh"


def test_release_version_extraction_removes_carriage_returns():
    script = RELEASE_SCRIPT.read_text(encoding="utf-8")

    assert "tr -d '\\r'" in script
    assert script.index("APP_VERSION") < script.index("tr -d '\\r'")
    assert script.index("tr -d '\\r'") < script.index("RELEASE_APK")


def test_standard_artifact_name_has_no_platform_suffix():
    script = RELEASE_SCRIPT.read_text(encoding="utf-8")

    assert (
        'RELEASE_APK="bin/${RELEASE_NAME}-v${APP_VERSION}.apk"' in script
    )
