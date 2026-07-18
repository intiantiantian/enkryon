from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIGNING_SCRIPT = (
    PROJECT_ROOT / "scripts" / "build-android-release.sh"
)
GITIGNORE = PROJECT_ROOT / ".gitignore"


def test_signing_secrets_are_ignored():
    ignore_patterns = {
        line.strip()
        for line in GITIGNORE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert {
        "*.jks",
        "*.keystore",
        "signing.env",
        "*.signing.env",
    } <= ignore_patterns


def test_release_helper_uses_private_ephemeral_password_prompts():
    script = SIGNING_SCRIPT.read_text(encoding="utf-8")

    assert (
        'DEFAULT_KEYSTORE="$HOME/keystores/enkryon-release.jks"'
        in script
    )
    assert 'DEFAULT_ALIAS="enkryon"' in script
    assert script.count('read -r -s -p "') == 2
    assert 'buildozer -v android release' in script
    assert 'trap cleanup EXIT HUP INT TERM' in script
    assert 'set -x' not in script
    assert 'android' not in _assigned_password_values(script)


def _assigned_password_values(script):
    values = []

    for line in script.splitlines():
        if "PASSWD=" not in line:
            continue

        values.append(line.split("=", 1)[1].strip().strip('"'))

    return values
