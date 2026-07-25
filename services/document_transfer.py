from pathlib import Path
from typing import NamedTuple, Optional


BACKUP_MIME_TYPE = "application/json"
EXPORT_REQUEST_CODE = 7101
IMPORT_REQUEST_CODE = 7102

TRANSFER_COMPLETED = "completed"
TRANSFER_CANCELLED = "cancelled"
TRANSFER_FAILED = "failed"


class DocumentTransferResult(NamedTuple):
    status: str
    content: Optional[str] = None
    error: Optional[str] = None


class _PendingTransfer(NamedTuple):
    operation: str
    callback: object
    content: Optional[str] = None


class DesktopDocumentTransfer:

    def __init__(self, save_picker=None, open_picker=None):
        self._save_picker = save_picker or self._choose_save_path
        self._open_picker = open_picker or self._choose_open_path


    def export_backup(
        self,
        serialized_backup,
        suggested_filename,
        callback,
    ):
        try:
            selected_path = self._save_picker(suggested_filename)

            if not selected_path:
                callback(
                    DocumentTransferResult(TRANSFER_CANCELLED)
                )
                return

            Path(selected_path).write_text(
                serialized_backup,
                encoding="utf-8",
                newline="",
            )
        except Exception as error:
            callback(
                DocumentTransferResult(
                    TRANSFER_FAILED,
                    error=str(error),
                )
            )
            return

        callback(DocumentTransferResult(TRANSFER_COMPLETED))


    def import_backup(self, callback):
        try:
            selected_path = self._open_picker()

            if not selected_path:
                callback(
                    DocumentTransferResult(TRANSFER_CANCELLED)
                )
                return

            serialized_backup = Path(selected_path).read_text(
                encoding="utf-8",
            )
        except Exception as error:
            callback(
                DocumentTransferResult(
                    TRANSFER_FAILED,
                    error=str(error),
                )
            )
            return

        callback(
            DocumentTransferResult(
                TRANSFER_COMPLETED,
                content=serialized_backup,
            )
        )


    @staticmethod
    def _choose_save_path(suggested_filename):
        from tkinter import Tk, filedialog

        root = Tk()
        root.withdraw()

        try:
            return filedialog.asksaveasfilename(
                title="Export Enkryon backup",
                initialfile=suggested_filename,
                defaultextension=".json",
                filetypes=(
                    ("Enkryon backups", "*.json"),
                    ("All files", "*.*"),
                ),
            )
        finally:
            root.destroy()


    @staticmethod
    def _choose_open_path():
        from tkinter import Tk, filedialog

        root = Tk()
        root.withdraw()

        try:
            return filedialog.askopenfilename(
                title="Restore Enkryon backup",
                filetypes=(
                    ("Enkryon backups", "*.json"),
                    ("All files", "*.*"),
                ),
            )
        finally:
            root.destroy()


class AndroidDocumentBridge:

    def __init__(
        self,
        activity_events=None,
        autoclass_function=None,
    ):
        if activity_events is None:
            from android import activity as activity_events

        if autoclass_function is None:
            from jnius import autoclass as autoclass_function

        self._activity_events = activity_events
        self._Intent = autoclass_function(
            "android.content.Intent"
        )
        self._Activity = autoclass_function(
            "android.app.Activity"
        )
        self._PythonActivity = autoclass_function(
            "org.kivy.android.PythonActivity"
        )
        self._OutputStreamWriter = autoclass_function(
            "java.io.OutputStreamWriter"
        )
        self._Scanner = autoclass_function("java.util.Scanner")
        self._activity = self._PythonActivity.mActivity


    @property
    def result_ok(self):
        return self._Activity.RESULT_OK


    def bind_activity_result(self, callback):
        self._activity_events.bind(on_activity_result=callback)


    def unbind_activity_result(self, callback):
        self._activity_events.unbind(on_activity_result=callback)


    def launch_export(self, request_code, suggested_filename):
        intent = self._Intent(self._Intent.ACTION_CREATE_DOCUMENT)
        intent.addCategory(self._Intent.CATEGORY_OPENABLE)
        intent.setType(BACKUP_MIME_TYPE)
        intent.putExtra(
            self._Intent.EXTRA_TITLE,
            suggested_filename,
        )
        self._activity.startActivityForResult(
            intent,
            request_code,
        )


    def launch_import(self, request_code):
        intent = self._Intent(self._Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(self._Intent.CATEGORY_OPENABLE)
        intent.setType(BACKUP_MIME_TYPE)
        self._activity.startActivityForResult(
            intent,
            request_code,
        )


    @staticmethod
    def result_uri(intent):
        return intent.getData()


    def write_text(self, uri, content):
        output_stream = (
            self._activity
            .getContentResolver()
            .openOutputStream(uri)
        )

        if output_stream is None:
            raise OSError("The selected document could not be opened.")

        writer = self._OutputStreamWriter(
            output_stream,
            "UTF-8",
        )

        try:
            writer.write(content)
        finally:
            writer.close()


    def read_text(self, uri):
        input_stream = (
            self._activity
            .getContentResolver()
            .openInputStream(uri)
        )

        if input_stream is None:
            raise OSError("The selected document could not be opened.")

        scanner = self._Scanner(input_stream, "UTF-8")
        scanner.useDelimiter(r"\A")

        try:
            if not scanner.hasNext():
                return ""

            return str(scanner.next())
        finally:
            scanner.close()


class AndroidDocumentTransfer:

    def __init__(self, bridge=None):
        self._bridge = bridge or AndroidDocumentBridge()
        self._pending_transfer = None
        self._activity_result_bound = False


    def export_backup(
        self,
        serialized_backup,
        suggested_filename,
        callback,
    ):
        pending_transfer = _PendingTransfer(
            operation="export",
            callback=callback,
            content=serialized_backup,
        )
        self._start_transfer(
            pending_transfer,
            lambda: self._bridge.launch_export(
                EXPORT_REQUEST_CODE,
                suggested_filename,
            ),
        )


    def import_backup(self, callback):
        pending_transfer = _PendingTransfer(
            operation="import",
            callback=callback,
        )
        self._start_transfer(
            pending_transfer,
            lambda: self._bridge.launch_import(
                IMPORT_REQUEST_CODE,
            ),
        )


    def _start_transfer(self, pending_transfer, launch):
        if self._pending_transfer is not None:
            pending_transfer.callback(
                DocumentTransferResult(
                    TRANSFER_FAILED,
                    error=(
                        "Another document transfer is already in "
                        "progress."
                    ),
                )
            )
            return

        self._pending_transfer = pending_transfer

        try:
            self._bridge.bind_activity_result(
                self._on_activity_result
            )
            self._activity_result_bound = True
            launch()
        except Exception as error:
            self._finish_transfer(
                DocumentTransferResult(
                    TRANSFER_FAILED,
                    error=str(error),
                )
            )


    def _on_activity_result(
        self,
        request_code,
        result_code,
        intent,
    ):
        if self._pending_transfer is None:
            return

        expected_request_code = {
            "export": EXPORT_REQUEST_CODE,
            "import": IMPORT_REQUEST_CODE,
        }[self._pending_transfer.operation]

        if request_code != expected_request_code:
            return

        if (
            result_code != self._bridge.result_ok
            or intent is None
        ):
            self._finish_transfer(
                DocumentTransferResult(TRANSFER_CANCELLED)
            )
            return

        try:
            uri = self._bridge.result_uri(intent)

            if uri is None:
                raise OSError(
                    "The selected document could not be opened."
                )

            if self._pending_transfer.operation == "export":
                self._bridge.write_text(
                    uri,
                    self._pending_transfer.content,
                )
                result = DocumentTransferResult(
                    TRANSFER_COMPLETED
                )
            else:
                result = DocumentTransferResult(
                    TRANSFER_COMPLETED,
                    content=self._bridge.read_text(uri),
                )
        except Exception as error:
            result = DocumentTransferResult(
                TRANSFER_FAILED,
                error=str(error),
            )

        self._finish_transfer(result)


    def _finish_transfer(self, result):
        pending_transfer = self._pending_transfer
        self._pending_transfer = None

        if self._activity_result_bound:
            self._bridge.unbind_activity_result(
                self._on_activity_result
            )
            self._activity_result_bound = False

        pending_transfer.callback(result)


def create_document_transfer(platform_name=None):
    if platform_name is None:
        from kivy.utils import platform as platform_name

    if platform_name == "android":
        return AndroidDocumentTransfer()

    return DesktopDocumentTransfer()
