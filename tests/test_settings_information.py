from pathlib import Path

from main import EnkryonApp, __version__


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_KV = PROJECT_ROOT / "kv" / "settings.kv"


def test_app_exposes_canonical_version():
    assert EnkryonApp.version == __version__


def test_settings_shows_about_local_data_and_privacy_information():
    settings_kv = SETTINGS_KV.read_text(encoding="utf-8")

    assert 'text: "About"' in settings_kv
    assert 'text: "Version {}".format(app.version)' in settings_kv
    assert 'text: "Data & Privacy"' in settings_kv
    assert "stored locally on this device" in settings_kv
    assert "require an account or upload your financial data" in settings_kv
    assert "Android automatic backup is currently disabled" in settings_kv
    assert "Backup and restore are not " in settings_kv
    assert 'text: "Clear All Data"' in settings_kv


def test_settings_information_uses_scrollable_dynamic_content():
    settings_kv = SETTINGS_KV.read_text(encoding="utf-8")
    scroll_content = settings_kv.split("ScrollView:", 1)[1]

    assert "do_scroll_x: False" in scroll_content
    assert "size_hint_y: None" in scroll_content
    assert "height: self.minimum_height" in scroll_content
    assert "text_size: self.width, None" in scroll_content
