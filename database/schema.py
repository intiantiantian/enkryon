from .account_repository import create_accounts_table
from .category_group_repository import create_category_groups_table
from .category_repository import create_categories_table
from .transaction_repository import create_transactions_table


def initialize_database():
    create_accounts_table()
    create_category_groups_table()
    create_categories_table()
    create_transactions_table()