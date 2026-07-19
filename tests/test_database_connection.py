from unittest.mock import Mock

import pytest

from database import connection as database_connection


def test_connect_database_enables_foreign_keys(monkeypatch):
    connection = Mock()
    connect = Mock(return_value=connection)
    get_database_path = Mock(return_value="database/test.db")
    monkeypatch.setattr(database_connection.sqlite3, "connect", connect)
    monkeypatch.setattr(
        database_connection,
        "get_database_path",
        get_database_path,
    )

    result = database_connection.connect_database()

    assert result is connection
    get_database_path.assert_called_once_with()
    connect.assert_called_once_with("database/test.db")
    connection.execute.assert_called_once_with(
        "PRAGMA foreign_keys = ON"
    )


def test_managed_connection_closes_after_success(monkeypatch):
    connection = Mock()
    connect_database = Mock(return_value=connection)
    monkeypatch.setattr(
        database_connection,
        "connect_database",
        connect_database,
    )

    with database_connection.managed_connection() as managed:
        assert managed is connection
        connection.close.assert_not_called()

    connect_database.assert_called_once_with()
    connection.commit.assert_not_called()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once_with()


def test_managed_connection_rolls_back_and_closes_after_failure(
    monkeypatch,
):
    connection = Mock()
    monkeypatch.setattr(
        database_connection,
        "connect_database",
        Mock(return_value=connection),
    )

    with pytest.raises(RuntimeError, match="operation failed"):
        with database_connection.managed_connection() as managed:
            assert managed is connection
            raise RuntimeError("operation failed")

    connection.commit.assert_not_called()
    connection.rollback.assert_called_once_with()
    connection.close.assert_called_once_with()
