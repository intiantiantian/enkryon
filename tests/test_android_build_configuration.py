import configparser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILDOZER_FILE = PROJECT_ROOT / "buildozer.spec"


ANDROID_REQUIREMENTS_FILE = (
    PROJECT_ROOT / "requirements-android.txt"
)


def load_app_config():
    config = configparser.ConfigParser(interpolation=None)
    config.read(BUILDOZER_FILE, encoding="utf-8")
    return config["app"]


def test_android_compatibility_versions_are_explicit():
    app_config = load_app_config()

    target_api = int(app_config["android.api"])
    minimum_api = int(app_config["android.minapi"])
    ndk_api = int(app_config["android.ndk_api"])

    assert target_api == 36
    assert minimum_api == 24
    assert app_config["android.ndk"] == "28"
    assert ndk_api == minimum_api
    assert minimum_api < target_api


def test_android_automatic_backup_is_disabled():
    app_config = load_app_config()

    assert app_config.getboolean("android.allow_backup") is False
    assert app_config.get("android.backup_rules") is None


def test_android_build_toolchain_versions_are_pinned():
    app_config = load_app_config()

    requirements = {
        line.strip()
        for line in ANDROID_REQUIREMENTS_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip() and not line.startswith("#")
    }

    assert app_config["p4a.branch"] == "v2026.05.09"
    assert requirements == {
        "buildozer==1.6.0",
        "Cython==0.29.37",
    }
