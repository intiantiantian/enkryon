from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_SCRIPT = PROJECT_ROOT / "scripts" / "build-android-release.sh"


def test_release_helper_accepts_build_tools_37_signer_label():
    script = RELEASE_SCRIPT.read_text(encoding="utf-8")

    assert (
        "sed -n 's/^.*certificate SHA-256 digest: //p'"
        in script
    )
    assert (
        'EXPECTED_CERTIFICATE_SHA256="e3d29b108a694aed7587fd995f00b022'
        '6497b566a6533ae847ef2371a012c43d"'
        in script
    )


def test_signer_parser_remains_before_artifact_copy():
    script = RELEASE_SCRIPT.read_text(encoding="utf-8")

    assert script.index("CERTIFICATE_SHA256") < script.index(
        'cp -- "$BUILT_APK" "$RELEASE_APK"'
    )
