from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager

from screens.dashboard import DashboardScreen
from screens.add_transaction import AddTransactionScreen
from screens.history import HistoryScreen
from screens.settings import SettingsScreen

from kivy.lang import Builder

class MyFinance(App):
    def build(self):

        Builder.load_file('kv/dashboard.kv')
        Builder.load_file('kv/add_transaction.kv')
        Builder.load_file('kv/history.kv')
        Builder.load_file('kv/settings.kv')

        screen_manager = ScreenManager()

        screen_manager.add_widget(DashboardScreen(name='dashboard'))
        screen_manager.add_widget(AddTransactionScreen(name='add_transaction'))
        screen_manager.add_widget(HistoryScreen(name='history'))
        screen_manager.add_widget(SettingsScreen(name='settings'))

        return screen_manager
    
if __name__ == '__main__':
    MyFinance().run()