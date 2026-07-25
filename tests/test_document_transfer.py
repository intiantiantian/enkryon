from types import SimpleNamespace
from unittest.mock import Mock

import services.document_transfer as document_transfer
from services.document_transfer import (
    AndroidDocumentBridge,
    AndroidDocumentTransfer,
    BACKUP_MIME_TYPE,
    DesktopDocumentTransfer,
    TRANSFER_CANCELLED,
    TRANSFER_COMPLETED,
    TRANSFER_FAILED,
)


class FakeIntent:

    ACTION_CREATE_DOCUMENT = "create"
    ACTION_OPEN_DOCUMENT = "open"
    CATEGORY_OPENABLE = "openable"
    EXTRA_TITLE = "title"

    def __init__(self, action):
        self.action = action
        self.categories = []
        self.mime_type = None
        self.extras = {}


    def addCategory(self, category):
        self.categories.append(category)


    def setType(self, mime_type):
        self.mime_type = mime_type


    def putExtra(self, name, value):
        self.extras[name] = value


class FakeContentResolver:

    def __init__(self):
        self.output_stream = SimpleNamespace(content=None)
        self.input_stream = SimpleNamespace(
            content='{"restored": true}\n'
        )
        self.output_uri = None
        self.input_uri = None


    def openOutputStream(self, uri):
        self.output_uri = uri
        return self.output_stream


    def openInputStream(self, uri):
        self.input_uri = uri
        return self.input_stream


class FakeCurrentActivity:

    def __init__(self):
        self.content_resolver = FakeContentResolver()
        self.started_activity = None


    def getContentResolver(self):
        return self.content_resolver


    def startActivityForResult(self, intent, request_code):
        self.started_activity = (intent, request_code)


class FakeOutputStreamWriter:

    def __init__(self, output_stream, encoding):
        self.output_stream = output_stream
        self.encoding = encoding
        self.closed = False


    def write(self, content):
        self.output_stream.content = content


    def close(self):
        self.closed = True


class FakeScanner:

    def __init__(self, input_stream, encoding):
        self.content = input_stream.content
        self.encoding = encoding
        self.delimiter = None
        self.closed = False


    def useDelimiter(self, delimiter):
        self.delimiter = delimiter


    def hasNext(self):
        return bool(self.content)


    def next(self):
        return self.content


    def close(self):
        self.closed = True


class FakeAndroidBridge:

    result_ok = -1

    def __init__(self):
        self.activity_result_callback = None
        self.launched_export = None
        self.launched_import = None
        self.written_document = None
        self.documents = {}
        self.unbind_count = 0


    def bind_activity_result(self, callback):
        self.activity_result_callback = callback


    def unbind_activity_result(self, callback):
        assert callback == self.activity_result_callback
        self.unbind_count += 1


    def launch_export(self, request_code, suggested_filename):
        self.launched_export = (
            request_code,
            suggested_filename,
        )


    def launch_import(self, request_code):
        self.launched_import = request_code


    @staticmethod
    def result_uri(intent):
        return intent.uri


    def write_text(self, uri, content):
        self.written_document = (uri, content)


    def read_text(self, uri):
        return self.documents[uri]


def test_desktop_transfer_writes_and_reads_exact_utf8(tmp_path):
    backup_path = tmp_path / "enkryon-backup.json"
    export_results = []
    import_results = []
    serialized_backup = '{"name": "Banco – Café"}\n'
    transfer = DesktopDocumentTransfer(
        save_picker=lambda _suggested_filename: backup_path,
        open_picker=lambda: backup_path,
    )

    transfer.export_backup(
        serialized_backup,
        "suggested.json",
        export_results.append,
    )
    transfer.import_backup(import_results.append)

    assert backup_path.read_bytes() == serialized_backup.encode(
        "utf-8"
    )
    assert export_results[0].status == TRANSFER_COMPLETED
    assert export_results[0].content is None
    assert import_results[0].status == TRANSFER_COMPLETED
    assert import_results[0].content == serialized_backup


def test_desktop_transfer_reports_cancellation():
    results = []
    transfer = DesktopDocumentTransfer(
        save_picker=lambda _suggested_filename: "",
        open_picker=lambda: None,
    )

    transfer.export_backup("backup", "backup.json", results.append)
    transfer.import_backup(results.append)

    assert [result.status for result in results] == [
        TRANSFER_CANCELLED,
        TRANSFER_CANCELLED,
    ]


def test_desktop_transfer_reports_file_error(tmp_path):
    results = []
    missing_path = tmp_path / "missing" / "backup.json"
    transfer = DesktopDocumentTransfer(
        save_picker=lambda _suggested_filename: missing_path,
    )

    transfer.export_backup(
        "backup",
        "backup.json",
        results.append,
    )

    assert results[0].status == TRANSFER_FAILED
    assert results[0].error


def test_android_bridge_configures_picker_and_content_streams():
    current_activity = FakeCurrentActivity()
    activity_events = SimpleNamespace(
        bind=Mock(),
        unbind=Mock(),
    )
    android_classes = {
        "android.content.Intent": FakeIntent,
        "android.app.Activity": SimpleNamespace(RESULT_OK=-1),
        "org.kivy.android.PythonActivity": SimpleNamespace(
            mActivity=current_activity
        ),
        "java.io.OutputStreamWriter": FakeOutputStreamWriter,
        "java.util.Scanner": FakeScanner,
    }
    bridge = AndroidDocumentBridge(
        activity_events=activity_events,
        autoclass_function=android_classes.__getitem__,
    )

    bridge.launch_export(7101, "enkryon-backup.json")

    export_intent, request_code = (
        current_activity.started_activity
    )
    assert request_code == 7101
    assert export_intent.action == FakeIntent.ACTION_CREATE_DOCUMENT
    assert export_intent.categories == [
        FakeIntent.CATEGORY_OPENABLE
    ]
    assert export_intent.mime_type == BACKUP_MIME_TYPE
    assert export_intent.extras == {
        FakeIntent.EXTRA_TITLE: "enkryon-backup.json"
    }

    bridge.launch_import(7102)

    import_intent, request_code = (
        current_activity.started_activity
    )
    assert request_code == 7102
    assert import_intent.action == FakeIntent.ACTION_OPEN_DOCUMENT
    assert import_intent.categories == [
        FakeIntent.CATEGORY_OPENABLE
    ]
    assert import_intent.mime_type == BACKUP_MIME_TYPE

    bridge.write_text("content://export", '{"backup": true}\n')
    restored_content = bridge.read_text("content://import")

    resolver = current_activity.content_resolver
    assert resolver.output_uri == "content://export"
    assert resolver.output_stream.content == '{"backup": true}\n'
    assert resolver.input_uri == "content://import"
    assert restored_content == '{"restored": true}\n'


def test_android_export_uses_create_document_and_writes_content():
    bridge = FakeAndroidBridge()
    results = []
    transfer = AndroidDocumentTransfer(bridge)

    transfer.export_backup(
        '{"backup": true}\n',
        "enkryon-backup.json",
        results.append,
    )

    assert bridge.launched_export == (
        document_transfer.EXPORT_REQUEST_CODE,
        "enkryon-backup.json",
    )

    bridge.activity_result_callback(
        document_transfer.EXPORT_REQUEST_CODE + 1,
        bridge.result_ok,
        SimpleNamespace(uri="ignored"),
    )
    assert results == []

    bridge.activity_result_callback(
        document_transfer.EXPORT_REQUEST_CODE,
        bridge.result_ok,
        SimpleNamespace(uri="content://exported"),
    )

    assert bridge.written_document == (
        "content://exported",
        '{"backup": true}\n',
    )
    assert results[0].status == TRANSFER_COMPLETED
    assert bridge.unbind_count == 1


def test_android_import_uses_open_document_and_reads_content():
    bridge = FakeAndroidBridge()
    bridge.documents["content://selected"] = (
        '{"backup": "restored"}\n'
    )
    results = []
    transfer = AndroidDocumentTransfer(bridge)

    transfer.import_backup(results.append)

    assert (
        bridge.launched_import
        == document_transfer.IMPORT_REQUEST_CODE
    )

    bridge.activity_result_callback(
        document_transfer.IMPORT_REQUEST_CODE,
        bridge.result_ok,
        SimpleNamespace(uri="content://selected"),
    )

    assert results[0].status == TRANSFER_COMPLETED
    assert results[0].content == '{"backup": "restored"}\n'
    assert bridge.unbind_count == 1


def test_android_transfer_reports_cancel_and_io_failure():
    cancel_bridge = FakeAndroidBridge()
    cancel_results = []
    cancel_transfer = AndroidDocumentTransfer(cancel_bridge)
    cancel_transfer.import_backup(cancel_results.append)

    cancel_bridge.activity_result_callback(
        document_transfer.IMPORT_REQUEST_CODE,
        0,
        None,
    )

    failing_bridge = FakeAndroidBridge()
    failing_bridge.write_text = Mock(
        side_effect=OSError("write failed")
    )
    failure_results = []
    failing_transfer = AndroidDocumentTransfer(failing_bridge)
    failing_transfer.export_backup(
        "backup",
        "backup.json",
        failure_results.append,
    )
    failing_bridge.activity_result_callback(
        document_transfer.EXPORT_REQUEST_CODE,
        failing_bridge.result_ok,
        SimpleNamespace(uri="content://failed"),
    )

    assert cancel_results[0].status == TRANSFER_CANCELLED
    assert failure_results[0].status == TRANSFER_FAILED
    assert failure_results[0].error == "write failed"


def test_android_transfer_rejects_concurrent_request():
    bridge = FakeAndroidBridge()
    first_results = []
    second_results = []
    transfer = AndroidDocumentTransfer(bridge)

    transfer.import_backup(first_results.append)
    transfer.export_backup(
        "backup",
        "backup.json",
        second_results.append,
    )

    assert first_results == []
    assert second_results[0].status == TRANSFER_FAILED
    assert "already in progress" in second_results[0].error


def test_transfer_factory_selects_platform_adapter(monkeypatch):
    android_adapter = object()
    android_constructor = Mock(return_value=android_adapter)
    monkeypatch.setattr(
        document_transfer,
        "AndroidDocumentTransfer",
        android_constructor,
    )

    assert isinstance(
        document_transfer.create_document_transfer("win"),
        DesktopDocumentTransfer,
    )
    assert (
        document_transfer.create_document_transfer("android")
        is android_adapter
    )
    android_constructor.assert_called_once_with()
