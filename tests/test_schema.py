from database import schema


def test_initialize_database_uses_dependency_order(monkeypatch):
    calls = []

    monkeypatch.setattr(
        schema,
        "create_accounts_table",
        lambda: calls.append("accounts"),
    )
    monkeypatch.setattr(
        schema,
        "create_category_groups_table",
        lambda: calls.append("category_groups"),
    )
    monkeypatch.setattr(
        schema,
        "create_categories_table",
        lambda: calls.append("categories"),
    )
    monkeypatch.setattr(
        schema,
        "create_transactions_table",
        lambda: calls.append("transactions"),
    )

    schema.initialize_database()

    assert calls == [
        "accounts",
        "category_groups",
        "categories",
        "transactions",
    ]