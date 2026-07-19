from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_SCRIPT = PROJECT_ROOT / "scripts" / "build-android-release.sh"


def test_release_helper_verifies_and_standardizes_artifact():
    script = RELEASE_SCRIPT.read_text(encoding="utf-8")

    assert (
        'EXPECTED_CERTIFICATE_SHA256="e3d29b108a694aed7587fd995f00b022'
        '6497b566a6533ae847ef2371a012c43d"'
        in script
    )
    assert (
        '"$APKSIGNER" verify --verbose --print-certs "$BUILT_APK"'
        in script
    )
    assert '"$ZIPALIGN" -c -P 16 -v 4 "$BUILT_APK"' in script
    assert (
        'RELEASE_APK="bin/${RELEASE_NAME}-v${APP_VERSION}.apk"'
        in script
    )
    assert 'RELEASE_CHECKSUM="${RELEASE_APK}.sha256"' in script
    assert 'sha256sum "$(basename "$RELEASE_APK")"' in script
    assert script.index(
        '"$APKSIGNER" verify --verbose --print-certs'
    ) < script.index(
        '"$ZIPALIGN" -c -P 16 -v 4'
    ) < script.index(
        'sha256sum "$(basename "$RELEASE_APK")"'
    )
