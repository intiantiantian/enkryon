import sqlite3

import pytest

from database import connection as database_connection
from database import account_repository
from database import category_group_repository
from database import category_repository
from database import transaction_repository
from database.schema import initialize_database
from database import interest_repository
from database import migrations
from database import transfer_repository


@pytest.fixture(autouse=True)
def test_database(tmp_path, monkeypatch):
    database_path = tmp_path / "test_database.db"

    def connect_test_database():
        connection = sqlite3.connect(database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    repositories = [
        database_connection,
        account_repository,
        category_group_repository,
        category_repository,
        interest_repository,
        migrations,
        transfer_repository,
        transaction_repository,
    ]

    for repository in repositories:
        monkeypatch.setattr(
            repository,
            "connect_database",
            connect_test_database,
            raising=False,
        )

    initialize_database()

    yield
