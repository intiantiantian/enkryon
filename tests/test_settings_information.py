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
    assert "Android automatic backup remains disabled" in settings_kv
    assert 'text: "Backup & Restore"' in settings_kv
    assert 'text: "Export Backup"' in settings_kv
    assert 'text: "Restore Backup"' in settings_kv
    assert "location you choose" in settings_kv
    assert "does not upload or sync" in settings_kv
    assert "fully validated and summarized" in settings_kv
    assert "on_release: root.export_backup()" in settings_kv
    assert "on_release: root.restore_backup()" in settings_kv
    assert 'text: "Clear All Data"' in settings_kv
    assert "offers to export a backup before deletion" in settings_kv


def test_settings_information_uses_scrollable_dynamic_content():
    settings_kv = SETTINGS_KV.read_text(encoding="utf-8")
    scroll_content = settings_kv.split("ScrollView:", 1)[1]

    assert "do_scroll_x: False" in scroll_content
    assert "size_hint_y: None" in scroll_content
    assert "height: self.minimum_height" in scroll_content
    assert "text_size: self.width, None" in scroll_content
