from configparser import ConfigParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_SPEC = PROJECT_ROOT / "buildozer.spec"


def load_app_configuration():
    parser = ConfigParser(interpolation=None)
    parser.read(BUILD_SPEC, encoding="utf-8")
    return parser["app"]


def comma_separated_values(value):
    return {
        item.strip()
        for item in value.split(",")
        if item.strip()
    }


def test_android_source_archive_excludes_development_directories():
    app = load_app_configuration()
    excluded_directories = comma_separated_values(
        app["source.exclude_dirs"]
    )

    assert {
        ".git",
        ".venv",
        ".buildozer",
        "bin",
        "tests",
        "docs",
        "__pycache__",
        ".pytest_cache",
    } <= excluded_directories


def test_android_source_archive_excludes_nonruntime_images():
    app = load_app_configuration()
    excluded_patterns = comma_separated_values(
        app["source.exclude_patterns"]
    )

    assert {
        "assets/screenshots/*/*.jpg",
        "assets/icon/*.png",
        "assets/splash/*.png",
    } <= excluded_patterns
