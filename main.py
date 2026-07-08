from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from screens.dashboard import DashboardScreen
from screens.add_transaction import AddTransactionScreen
from screens.settings import SettingsScreen
from screens.accounts import AccountsScreen
from screens.categories import CategoriesScreen
from screens.transactions import TransactionsScreen

from database.transaction_repository import create_transactions_table
from database.account_repository import create_accounts_table
from database.category_group_repository import create_category_groups_table, insert_category_group
from database.category_repository import create_categories_table, insert_category

class MyFinance(MDApp):
    def build(self):

        Builder.load_file('kv/dashboard.kv')
        Builder.load_file('kv/add_transaction.kv')
        Builder.load_file('kv/settings.kv')
        Builder.load_file('kv/accounts.kv')
        Builder.load_file('kv/categories.kv')
        Builder.load_file('kv/transactions.kv')

        create_transactions_table()
        create_accounts_table()
        create_category_groups_table()
        create_categories_table()

        screen_manager = ScreenManager()

        screen_manager.add_widget(DashboardScreen(name='dashboard'))
        screen_manager.add_widget(AddTransactionScreen(name='add_transaction'))
        screen_manager.add_widget(SettingsScreen(name='settings'))
        screen_manager.add_widget(AccountsScreen(name='accounts'))
        screen_manager.add_widget(CategoriesScreen(name='categories'))
        screen_manager.add_widget(TransactionsScreen(name='transactions'))

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Cyan"

        return screen_manager
    
if __name__ == '__main__':
    MyFinance().run()