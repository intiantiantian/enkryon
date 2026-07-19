from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from screens.dashboard import DashboardScreen
from screens.add_transaction import AddTransactionScreen
from screens.settings import SettingsScreen
from screens.accounts import AccountsScreen
from screens.categories import CategoriesScreen
from screens.transactions import TransactionsScreen

from database.schema import initialize_database

from theme.app_theme import apply_app_theme

from widgets.buttons import (
    EnkryonFilterButton,
    EnkryonPrimaryButton,
    EnkryonSecondaryButton,
)

_ = (
    EnkryonFilterButton,
    EnkryonPrimaryButton,
    EnkryonSecondaryButton,
)

__version__ = "0.4.8"

class EnkryonApp(MDApp):
    def build(self):

        apply_app_theme(self)

        Builder.load_file('kv/widgets.kv')
        Builder.load_file('kv/dashboard.kv')
        Builder.load_file('kv/add_transaction.kv')
        Builder.load_file('kv/settings.kv')
        Builder.load_file('kv/accounts.kv')
        Builder.load_file('kv/categories.kv')
        Builder.load_file('kv/transactions.kv')
        Builder.load_file('kv/date_time_pickers.kv')
        Builder.load_file('kv/input_dialog.kv')

        initialize_database()

        screen_manager = ScreenManager()

        screen_manager.add_widget(DashboardScreen(name='dashboard'))
        screen_manager.add_widget(AddTransactionScreen(name='add_transaction'))
        screen_manager.add_widget(SettingsScreen(name='settings'))
        screen_manager.add_widget(AccountsScreen(name='accounts'))
        screen_manager.add_widget(CategoriesScreen(name='categories'))
        screen_manager.add_widget(TransactionsScreen(name='transactions'))

        return screen_manager
    
if __name__ == '__main__':
    EnkryonApp().run()