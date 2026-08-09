from database.account_repository import insert_account
from database.category_group_repository import insert_category_group
from database.category_repository import insert_category
from database.interest_repository import (
    get_interest_accruals,
    get_interest_profiles,
    insert_interest_profile,
)
from database.transaction_repository import (
    get_current_balance_centavos,
    get_transaction_by_id,
    insert_transaction,
)
from services.interest_services import (
    generate_missing_interest_accruals,
    reconcile_interest_credit,
    remove_interest_tracking,
)


def seed_reconciled_interest():
    assert insert_account("Savings") is True
    assert insert_category_group("Income", "income") == (True, None)
    assert insert_category(1, "Salary") == (True, None)
    assert insert_category(1, "Bank Interest") == (True, None)
    assert insert_transaction(
        1,
        1_000_000,
        1,
        "2026-08-01 09:00:00",
        None,
    ) is True
    profile_id = insert_interest_profile(
        1,
        3_650_000,
        "2026-08-02",
        enabled=True,
    )
    assert profile_id is not False
    generate_missing_interest_accruals(1, "2026-08-03")
    result = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=250,
        credit_date="2026-08-03",
        category_id=2,
    )
    assert result.success is True
    return result.posted_transaction_id


def test_remove_interest_purges_tracking_but_preserves_posted_income():
    transaction_id = seed_reconciled_interest()

    result = remove_interest_tracking(1)

    assert result.success is True
    assert result.removed_profiles == 1
    assert result.removed_accruals == 2
    assert get_interest_profiles(1) == []
    assert get_interest_accruals(1) == []

    posted = get_transaction_by_id(transaction_id)
    assert posted is not None
    assert posted.amount_centavos == 250
    assert posted.transaction_type == "income"
    assert posted.posting_status == "posted"
    assert get_current_balance_centavos(1) == 1_000_250


def test_remove_interest_without_configuration_is_non_destructive():
    assert insert_account("Savings") is True

    result = remove_interest_tracking(1)

    assert result.success is False
    assert "no interest tracking" in result.message.lower()
    assert get_interest_profiles(1) == []
    assert get_interest_accruals(1) == []
