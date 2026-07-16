from database import schema


def test_initialize_database_runs_migrations(monkeypatch):
    calls = []

    monkeypatch.setattr(
        schema,
        "run_migrations",
        lambda: calls.append("migrations"),
    )

    schema.initialize_database()

    assert calls == ["migrations"]