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


def test_clear_database_deletes_interest_profiles_and_accruals():
    from database.interest_repository import (
        get_interest_accruals,
        get_interest_profiles,
        insert_interest_accrual,
        insert_interest_profile,
    )

    insert_account("Savings")
    profile_id = insert_interest_profile(
        account_id=1,
        annual_rate_micros=1_000_000,
        effective_from="2026-08-01",
    )
    assert profile_id is not False
    assert insert_interest_accrual(
        account_id=1,
        interest_profile_id=profile_id,
        accrual_date="2026-08-02",
        closing_balance_centavos=10_000,
        annual_rate_micros=1_000_000,
        accrued_whole_centavos=0,
        accrued_remainder_numerator=10_000_000_000,
    ) is not False

    assert clear_database() is True
    assert get_interest_accruals(1) == []
    assert get_interest_profiles(1) == []
    assert get_all_accounts() == []
