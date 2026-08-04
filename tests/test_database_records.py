from database.records import (
    AccountRecord,
    CategoryGroupRecord,
    CategoryRecord,
    TransferRecord,
    TransactionDetailRecord,
    TransactionListRecord,
)


def test_account_record_exposes_named_fields():
    account = AccountRecord(account_id=2, name="Cash")

    assert account.account_id == 2
    assert account.name == "Cash"


def test_category_group_record_exposes_named_fields():
    group = CategoryGroupRecord(
        group_id=5,
        name="Food",
        transaction_type="expense",
    )

    assert group.group_id == 5
    assert group.name == "Food"
    assert group.transaction_type == "expense"


def test_category_record_exposes_named_fields():
    category = CategoryRecord(
        category_id=8,
        group_id=5,
        name="Dining",
        group_name="Food",
        transaction_type="expense",
    )

    assert category.category_id == 8
    assert category.group_id == 5
    assert category.name == "Dining"
    assert category.group_name == "Food"
    assert category.transaction_type == "expense"


def test_transaction_list_record_exposes_named_fields():
    transaction = TransactionListRecord(
        transaction_id=17,
        account_name="Cash",
        group_name="Food",
        category_name="Dining",
        amount_centavos=12345,
        date_time="2026-07-19 19:30:00",
        notes="Dinner",
        transaction_type="expense",
    )

    assert transaction.transaction_id == 17
    assert transaction.account_name == "Cash"
    assert transaction.group_name == "Food"
    assert transaction.category_name == "Dining"
    assert transaction.amount_centavos == 12345
    assert transaction.date_time == "2026-07-19 19:30:00"
    assert transaction.notes == "Dinner"
    assert transaction.transaction_type == "expense"


def test_transaction_detail_record_exposes_named_fields():
    transaction = TransactionDetailRecord(
        transaction_id=17,
        account_id=2,
        amount_centavos=12345,
        category_id=8,
        date_time="2026-07-19 19:30:00",
        notes=None,
        account_name="Cash",
        category_name="Dining",
        group_id=5,
        group_name="Food",
        transaction_type="expense",
    )

    assert transaction.transaction_id == 17
    assert transaction.account_id == 2
    assert transaction.amount_centavos == 12345
    assert transaction.category_id == 8
    assert transaction.date_time == "2026-07-19 19:30:00"
    assert transaction.notes is None
    assert transaction.account_name == "Cash"
    assert transaction.category_name == "Dining"
    assert transaction.group_id == 5
    assert transaction.group_name == "Food"
    assert transaction.transaction_type == "expense"


def test_transfer_record_exposes_named_fields():
    transfer = TransferRecord(
        transfer_id=23,
        source_account_id=2,
        destination_account_id=7,
        amount_centavos=10025,
        date_time="2026-08-04 14:30:00",
        notes="Emergency fund",
        source_account_name="Cash",
        destination_account_name="Savings",
    )

    assert transfer.transfer_id == 23
    assert transfer.source_account_id == 2
    assert transfer.destination_account_id == 7
    assert transfer.amount_centavos == 10025
    assert transfer.date_time == "2026-08-04 14:30:00"
    assert transfer.notes == "Emergency fund"
    assert transfer.source_account_name == "Cash"
    assert transfer.destination_account_name == "Savings"
