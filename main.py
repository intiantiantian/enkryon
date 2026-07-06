from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from screens.dashboard import DashboardScreen
from screens.add_transaction import AddTransactionScreen
from screens.history import HistoryScreen
from screens.settings import SettingsScreen
from screens.accounts import AccountsScreen

from database.transaction_repository import create_transactions_table
from database.account_repository import create_accounts_table


class MyFinance(MDApp):
    def build(self):

        Builder.load_file('kv/dashboard.kv')
        Builder.load_file('kv/add_transaction.kv')
        Builder.load_file('kv/history.kv')
        Builder.load_file('kv/settings.kv')
        Builder.load_file('kv/accounts.kv')

        create_transactions_table()
        create_accounts_table()

        screen_manager = ScreenManager()

        screen_manager.add_widget(DashboardScreen(name='dashboard'))
        screen_manager.add_widget(AddTransactionScreen(name='add_transaction'))
        screen_manager.add_widget(HistoryScreen(name='history'))
        screen_manager.add_widget(SettingsScreen(name='settings'))
        screen_manager.add_widget(AccountsScreen(name='accounts'))

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"

        return screen_manager
    
if __name__ == '__main__':
    MyFinance().run()