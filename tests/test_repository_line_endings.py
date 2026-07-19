from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GITATTRIBUTES = PROJECT_ROOT / ".gitattributes"
SCRIPTS_DIRECTORY = PROJECT_ROOT / "scripts"


def test_shell_scripts_are_checked_out_with_lf_line_endings():
    attributes = GITATTRIBUTES.read_text(encoding="utf-8").splitlines()

    assert "*.sh text eol=lf" in attributes

    shell_scripts = sorted(SCRIPTS_DIRECTORY.glob("*.sh"))
    assert shell_scripts

    for shell_script in shell_scripts:
        assert b"\r\n" not in shell_script.read_bytes(), (
            f"{shell_script.relative_to(PROJECT_ROOT)} must use LF"
        )
