from database.account_repository import get_all_accounts, insert_account
from database.category_group_repository import (
    get_all_category_groups,
    insert_category_group,
)
from database.category_repository import (
    get_all_categories,
    insert_category,
)
from database.settings_repository import clear_database
from database.transaction_repository import (
    get_transactions,
    insert_transaction,
)


def test_clear_database_deletes_all_user_data():
    insert_account("Cash")
    insert_category_group("Food", "expense")
    insert_category(1, "Dining")
    insert_transaction(
        account_id=1,
        amount_centavos=12345,
        category_id=1,
        date_time="2026-07-20 12:00:00",
        notes="Lunch",
    )

    result = clear_database()

    assert result is True
    assert get_transactions() == []
    assert get_all_categories() == []
    assert get_all_category_groups() == []
    assert get_all_accounts() == []
