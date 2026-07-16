from utils.transaction_payload import build_transaction_payload


def test_build_transaction_payload_with_notes():
    payload = build_transaction_payload(
        account_id=1,
        amount="250.75",
        category_id=2,
        date_label="2026-07-15",
        time_label="03:30 PM",
        notes_label="Lunch",
    )

    assert payload == {
        "account_id": 1,
        "amount_centavos": 25075,
        "category_id": 2,
        "date_time": "2026-07-15 15:30:00",
        "notes": "Lunch",
    }


def test_build_transaction_payload_with_default_notes_label():
    payload = build_transaction_payload(
        account_id=1,
        amount="100",
        category_id=2,
        date_label="2026-07-15",
        time_label="08:05 AM",
        notes_label="Add notes",
    )

    assert payload["notes"] == ""