from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

from datetime import datetime, timezone

import pytest

from screens.settings import SettingsScreen

from services.backup_restorer import BackupRestoreError
from services.backup_validator import BackupValidationError
from services.document_transfer import (
    DocumentTransferResult,
    TRANSFER_CANCELLED,
    TRANSFER_COMPLETED,
    TRANSFER_FAILED,
)


EXPORTED_AT = datetime(
    2026,
    7,
    25,
    12,
    30,
    tzinfo=timezone.utc,
)


@pytest.mark.parametrize(
    ("repository_result", "expected_message"),
    [
        (True, "All data has been deleted."),
        (False, "Data could not be deleted."),
    ],
)
def test_clear_data_renders_repository_result(
    monkeypatch,
    repository_result,
    expected_message,
):
    settings_module = import_module("screens.settings")
    clear_database = Mock(return_value=repository_result)
    show_snackbar = Mock()
    monkeypatch.setattr(
        settings_module,
        "clear_database",
        clear_database,
    )
    monkeypatch.setattr(
        settings_module,
        "show_snackbar",
        show_snackbar,
    )

    dashboard = SimpleNamespace(load_dashboard=Mock())
    manager = SimpleNamespace(
        current="settings",
        get_screen=Mock(return_value=dashboard),
    )
    screen = SimpleNamespace(
        close_clear_data_dialog=Mock(),
        manager=manager,
    )

    SettingsScreen.perform_clear_data(screen)

    clear_database.assert_called_once_with()
    screen.close_clear_data_dialog.assert_called_once_with()
    show_snackbar.assert_called_once_with(expected_message)

    if repository_result:
        manager.get_screen.assert_called_once_with("dashboard")
        dashboard.load_dashboard.assert_called_once_with()
        assert manager.current == "dashboard"
    else:
        manager.get_screen.assert_not_called()
        dashboard.load_dashboard.assert_not_called()
        assert manager.current == "settings"


def test_export_backup_creates_timestamped_document(monkeypatch):
    settings_module = import_module("screens.settings")
    serialized_backup = '{"format": "enkryon-backup"}\n'
    export_backup_json = Mock(return_value=serialized_backup)
    document_transfer = SimpleNamespace(export_backup=Mock())
    export_callback = Mock()
    screen = SimpleNamespace(
        _get_document_transfer=Mock(
            return_value=document_transfer
        ),
        _handle_export_result=export_callback,
    )
    monkeypatch.setattr(
        settings_module,
        "export_backup_json",
        export_backup_json,
    )
    monkeypatch.setattr(
        settings_module,
        "datetime",
        SimpleNamespace(now=Mock(return_value=EXPORTED_AT)),
    )
    monkeypatch.setattr(
        settings_module.App,
        "get_running_app",
        Mock(return_value=SimpleNamespace(version="0.6.0")),
    )

    SettingsScreen.export_backup(screen)

    export_backup_json.assert_called_once_with(
        app_version="0.6.0",
        exported_at=EXPORTED_AT,
    )
    document_transfer.export_backup.assert_called_once_with(
        serialized_backup,
        "enkryon-backup-20260725-123000.json",
        export_callback,
    )


@pytest.mark.parametrize(
    ("status", "expected_message"),
    [
        (TRANSFER_COMPLETED, "Backup exported successfully."),
        (TRANSFER_CANCELLED, "Backup export cancelled."),
        (TRANSFER_FAILED, "Backup could not be saved."),
    ],
)
def test_export_result_renders_transfer_status(
    monkeypatch,
    status,
    expected_message,
):
    settings_module = import_module("screens.settings")
    show_snackbar = Mock()
    monkeypatch.setattr(
        settings_module,
        "show_snackbar",
        show_snackbar,
    )

    SettingsScreen._handle_export_result(
        SimpleNamespace(),
        DocumentTransferResult(status),
    )

    show_snackbar.assert_called_once_with(expected_message)


def test_import_backup_validates_and_previews_selected_document(
    monkeypatch,
):
    settings_module = import_module("screens.settings")
    preview = SimpleNamespace(
        app_version="0.6.0",
        database_version=3,
        exported_at="2026-07-25T12:30:00Z",
        record_counts={
            "accounts": 2,
            "category_groups": 3,
            "categories": 4,
            "transactions": 5,
        },
        total_records=14,
    )
    validated_backup = SimpleNamespace(preview=preview)
    validate_backup_json = Mock(return_value=validated_backup)
    open_confirmation = Mock()
    perform_restore = Mock()
    close_restore_dialog = Mock()
    screen = SimpleNamespace(
        pending_restore=None,
        _open_confirmation_dialog=open_confirmation,
        perform_restore=perform_restore,
        close_restore_dialog=close_restore_dialog,
    )
    monkeypatch.setattr(
        settings_module,
        "validate_backup_json",
        validate_backup_json,
    )

    SettingsScreen._handle_import_result(
        screen,
        DocumentTransferResult(
            TRANSFER_COMPLETED,
            content='{"format": "enkryon-backup"}\n',
        ),
    )

    validate_backup_json.assert_called_once_with(
        '{"format": "enkryon-backup"}\n'
    )
    assert screen.pending_restore is validated_backup
    call = open_confirmation.call_args
    assert call.kwargs["title"] == "Restore Backup?"
    assert call.kwargs["confirm_text"] == "Restore"
    assert call.kwargs["confirm_callback"] is perform_restore
    assert call.kwargs["cancel_callback"] is close_restore_dialog
    assert "Accounts: 2" in call.kwargs["message"]
    assert "Transactions: 5" in call.kwargs["message"]
    assert "Total records: 14" in call.kwargs["message"]
    assert "permanently replaces" in call.kwargs["message"]


@pytest.mark.parametrize(
    ("result", "validation_error", "expected_message"),
    [
        (
            DocumentTransferResult(TRANSFER_CANCELLED),
            False,
            "Backup selection cancelled.",
        ),
        (
            DocumentTransferResult(
                TRANSFER_FAILED,
                error="read failed",
            ),
            False,
            "Backup could not be opened.",
        ),
        (
            DocumentTransferResult(
                TRANSFER_COMPLETED,
                content="invalid",
            ),
            True,
            "The selected file is not a valid Enkryon backup.",
        ),
    ],
)
def test_import_backup_rejects_unusable_selection(
    monkeypatch,
    result,
    validation_error,
    expected_message,
):
    settings_module = import_module("screens.settings")
    validate_backup_json = Mock()
    show_snackbar = Mock()

    if validation_error:
        validate_backup_json.side_effect = BackupValidationError()

    monkeypatch.setattr(
        settings_module,
        "validate_backup_json",
        validate_backup_json,
    )
    monkeypatch.setattr(
        settings_module,
        "show_snackbar",
        show_snackbar,
    )
    screen = SimpleNamespace(
        pending_restore=None,
        _open_confirmation_dialog=Mock(),
    )

    SettingsScreen._handle_import_result(screen, result)

    screen._open_confirmation_dialog.assert_not_called()
    show_snackbar.assert_called_once_with(expected_message)
    assert screen.pending_restore is None


def test_restore_backup_refreshes_dashboard_after_success(monkeypatch):
    settings_module = import_module("screens.settings")
    validated_backup = object()
    restore_validated_backup = Mock()
    show_snackbar = Mock()
    dashboard = SimpleNamespace(load_dashboard=Mock())
    manager = SimpleNamespace(
        current="settings",
        get_screen=Mock(return_value=dashboard),
    )
    screen = SimpleNamespace(
        pending_restore=validated_backup,
        close_restore_dialog=Mock(),
        manager=manager,
    )
    monkeypatch.setattr(
        settings_module,
        "restore_validated_backup",
        restore_validated_backup,
    )
    monkeypatch.setattr(
        settings_module,
        "show_snackbar",
        show_snackbar,
    )

    SettingsScreen.perform_restore(screen)

    restore_validated_backup.assert_called_once_with(validated_backup)
    screen.close_restore_dialog.assert_called_once_with()
    manager.get_screen.assert_called_once_with("dashboard")
    dashboard.load_dashboard.assert_called_once_with()
    assert manager.current == "dashboard"
    show_snackbar.assert_called_once_with(
        "Backup restored successfully."
    )


@pytest.mark.parametrize(
    "restore_error",
    [
        BackupValidationError(),
        BackupRestoreError(),
    ],
)
def test_restore_failure_keeps_current_screen_and_reports_rollback(
    monkeypatch,
    restore_error,
):
    settings_module = import_module("screens.settings")
    restore_validated_backup = Mock(side_effect=restore_error)
    show_snackbar = Mock()
    manager = SimpleNamespace(
        current="settings",
        get_screen=Mock(),
    )
    screen = SimpleNamespace(
        pending_restore=object(),
        close_restore_dialog=Mock(),
        manager=manager,
    )
    monkeypatch.setattr(
        settings_module,
        "restore_validated_backup",
        restore_validated_backup,
    )
    monkeypatch.setattr(
        settings_module,
        "show_snackbar",
        show_snackbar,
    )

    SettingsScreen.perform_restore(screen)

    screen.close_restore_dialog.assert_called_once_with()
    manager.get_screen.assert_not_called()
    assert manager.current == "settings"
    show_snackbar.assert_called_once_with(
        "Backup could not be restored. "
        "Your current data was not changed."
    )
