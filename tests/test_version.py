import ast
import configparser
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_FILE = PROJECT_ROOT / "main.py"
BUILDOZER_FILE = PROJECT_ROOT / "buildozer.spec"
README_FILE = PROJECT_ROOT / "README.md"


def get_canonical_version():
    syntax_tree = ast.parse(
        MAIN_FILE.read_text(encoding="utf-8")
    )

    for statement in syntax_tree.body:
        if not isinstance(statement, ast.Assign):
            continue

        for target in statement.targets:
            if (
                isinstance(target, ast.Name)
                and target.id == "__version__"
            ):
                return ast.literal_eval(statement.value)

    raise AssertionError(
        "main.py does not define __version__."
    )


def test_canonical_version_has_numeric_release_format():
    version = get_canonical_version()

    assert re.fullmatch(r"\d+\.\d+\.\d+", version)


def test_buildozer_reads_version_from_main():
    config = configparser.ConfigParser(
        interpolation=None
    )
    config.read(BUILDOZER_FILE, encoding="utf-8")

    app_config = config["app"]

    assert app_config.get("version") is None
    assert app_config["version.regex"] == (
        '__version__ = [\'"](.*)[\'"]'
    )
    assert app_config["version.filename"] == (
        "%(source.dir)s/main.py"
    )


def test_readme_apk_filename_matches_canonical_version():
    version = get_canonical_version()
    readme = README_FILE.read_text(encoding="utf-8")

    assert f"Enkryon-v{version}.apk" in readme