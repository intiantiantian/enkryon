from datetime import datetime, timezone

from kivy.app import App
from kivy.uix.screenmanager import Screen

from database.settings_repository import clear_database
from services.backup_exporter import export_backup_json
from services.backup_restorer import (
    BackupRestoreError,
    restore_validated_backup,
)
from services.backup_validator import (
    BackupValidationError,
    validate_backup_json,
)
from services.document_transfer import (
    TRANSFER_CANCELLED,
    TRANSFER_COMPLETED,
    create_document_transfer,
)
from utils.snackbar import show_snackbar

from widgets.overlays import EnkryonConfirmationDialog


class SettingsScreen(Screen):

    dialog = None
    document_transfer = None
    pending_restore = None

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'


    def _get_document_transfer(self):
        if self.document_transfer is None:
            self.document_transfer = create_document_transfer()

        return self.document_transfer


    def _open_confirmation_dialog(
        self,
        *,
        title,
        message,
        confirm_text,
        confirm_callback,
        cancel_callback,
        cancel_text="Cancel",
    ):
        self.dialog = EnkryonConfirmationDialog(
            title=title,
            message=message,
            confirm_text=confirm_text,
            confirm_callback=confirm_callback,
            cancel_callback=cancel_callback,
            cancel_text=cancel_text,
        )
        self.dialog.open()


    def _close_confirmation_dialog(self):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None


    def export_backup(self, result_callback=None):
        if result_callback is None:
            result_callback = self._handle_export_result

        exported_at = datetime.now(timezone.utc)

        try:
            serialized_backup = export_backup_json(
                app_version=App.get_running_app().version,
                exported_at=exported_at,
            )
            self._get_document_transfer().export_backup(
                serialized_backup,
                (
                    "enkryon-backup-"
                    f"{exported_at.strftime('%Y%m%d-%H%M%S')}.json"
                ),
                result_callback,
            )
        except Exception:
            show_snackbar("Backup could not be created.")


    def _handle_export_result(self, result):
        if result.status == TRANSFER_COMPLETED:
            show_snackbar("Backup exported successfully.")
        elif result.status == TRANSFER_CANCELLED:
            show_snackbar("Backup export cancelled.")
        else:
            show_snackbar("Backup could not be saved.")


    def restore_backup(self):
        try:
            self._get_document_transfer().import_backup(
                self._handle_import_result
            )
        except Exception:
            show_snackbar("Backup could not be opened.")


    def _handle_import_result(self, result):
        if result.status == TRANSFER_CANCELLED:
            show_snackbar("Backup selection cancelled.")
            return

        if result.status != TRANSFER_COMPLETED:
            show_snackbar("Backup could not be opened.")
            return

        try:
            validated_backup = validate_backup_json(result.content)
        except BackupValidationError:
            show_snackbar(
                "The selected file is not a valid Enkryon backup."
            )
            return

        self.pending_restore = validated_backup
        preview = validated_backup.preview
        counts = preview.record_counts
        self._open_confirmation_dialog(
            title="Restore Backup?",
            message=(
                f"Created: {preview.exported_at}\n"
                f"Enkryon version: {preview.app_version}\n"
                f"Database version: {preview.database_version}\n\n"
                f"Accounts: {counts['accounts']}\n"
                f"Category groups: {counts['category_groups']}\n"
                f"Categories: {counts['categories']}\n"
                f"Transactions: {counts['transactions']}\n"
                f"Total records: {preview.total_records}\n\n"
                "Restoring permanently replaces all accounts, "
                "categories, and transactions currently stored on "
                "this device."
            ),
            confirm_text="Restore",
            confirm_callback=self.perform_restore,
            cancel_callback=self.close_restore_dialog,
        )


    def close_restore_dialog(self, *args):
        self.pending_restore = None
        self._close_confirmation_dialog()


    def perform_restore(self):
        validated_backup = self.pending_restore

        if validated_backup is None:
            self.close_restore_dialog()
            show_snackbar("No backup is ready to restore.")
            return

        try:
            restore_validated_backup(validated_backup)
        except (BackupValidationError, BackupRestoreError):
            self.close_restore_dialog()
            show_snackbar(
                "Backup could not be restored. "
                "Your current data was not changed."
            )
            return

        self.close_restore_dialog()

        dashboard = self.manager.get_screen("dashboard")
        dashboard.load_dashboard()

        self.manager.current = "dashboard"
        show_snackbar("Backup restored successfully.")


    def clear_data(self):
        self._open_confirmation_dialog(
            title="Back Up Before Deleting?",
            message=(
                "Clear All Data permanently deletes every account, "
                "category, and transaction. Export a backup before "
                "continuing so these records can be restored later, "
                "or skip the backup to continue to the final deletion "
                "confirmation."
            ),
            confirm_text="Export Backup",
            confirm_callback=self.export_backup_before_clear_data,
            cancel_text="Skip Backup",
            cancel_callback=self.skip_backup_before_clear_data,
        )


    def export_backup_before_clear_data(self):
        self._close_confirmation_dialog()
        self.export_backup(self._handle_pre_clear_export_result)


    def _handle_pre_clear_export_result(self, result):
        if result.status == TRANSFER_COMPLETED:
            show_snackbar("Backup exported successfully.")
            self._open_clear_data_confirmation()
        elif result.status == TRANSFER_CANCELLED:
            show_snackbar(
                "Backup export cancelled. No data was deleted."
            )
        else:
            show_snackbar(
                "Backup could not be saved. No data was deleted."
            )


    def skip_backup_before_clear_data(self, *args):
        self._close_confirmation_dialog()
        self._open_clear_data_confirmation()


    def _open_clear_data_confirmation(self):
        self._open_confirmation_dialog(
            title="Clear All Data?",
            message=(
                "This permanently deletes all accounts, "
                "categories, and transactions. This action "
                "cannot be undone."
            ),
            confirm_text="Delete All",
            confirm_callback=self.perform_clear_data,
            cancel_text="Cancel",
            cancel_callback=self.close_clear_data_dialog,
        )


    def close_clear_data_dialog(self, *args):
        self._close_confirmation_dialog()


    def perform_clear_data(self):
        cleared = clear_database()
        self.close_clear_data_dialog()

        if not cleared:
            show_snackbar("Data could not be deleted.")
            return

        dashboard = self.manager.get_screen("dashboard")
        dashboard.load_dashboard()

        self.manager.current = "dashboard"
        show_snackbar("All data has been deleted.")
