import sqlite3

import pytest

from database import account_repository
from database import category_group_repository
from database import category_repository
from database import settings_repository
from database import transaction_repository


@pytest.fixture(autouse=True)
def test_database(tmp_path, monkeypatch):
    database_path = tmp_path / "test_database.db"

    def connect_test_database():
        connection = sqlite3.connect(database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    repositories = [
        account_repository,
        category_group_repository,
        category_repository,
        settings_repository,
        transaction_repository,
    ]

    for repository in repositories:
        monkeypatch.setattr(
            repository,
            "connect_database",
            connect_test_database,
            raising=False,
        )

    account_repository.create_accounts_table()
    category_group_repository.create_category_groups_table()
    category_repository.create_categories_table()
    transaction_repository.create_transactions_table()

    yield