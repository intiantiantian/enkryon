from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window

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
from widgets.overlays import (
    EnkryonConfirmationDialog,
    EnkryonOverlay,
    EnkryonOverlayCard,
    EnkryonSelectionOption,
    EnkryonSelectionPanel,
)

_ = (
    EnkryonFilterButton,
    EnkryonPrimaryButton,
    EnkryonSecondaryButton,
    EnkryonConfirmationDialog,
    EnkryonOverlay,
    EnkryonOverlayCard,
    EnkryonSelectionOption,
    EnkryonSelectionPanel,
)

__version__ = "1.0.0"

class EnkryonApp(MDApp):

    BACK_KEY = 27

    def on_start(self):
        Window.bind(on_key_down=self.handle_back_button)


    def on_stop(self):
        Window.unbind(on_key_down=self.handle_back_button)


    def handle_back_button(self, _window, key, *_args):
        if key != self.BACK_KEY:
            return False

        if EnkryonOverlay.dismiss_active(Window):
            return True

        navigation_method = {
            "accounts": "go_back",
            "categories": "go_back",
            "add_transaction": "go_to_dashboard",
            "transactions": "go_to_dashboard",
            "settings": "go_to_dashboard",
        }.get(self.root.current)

        if navigation_method is None:
            return False

        current_screen = self.root.current_screen
        getattr(current_screen, navigation_method)()
        return True


    version = __version__


    def build(self):

        apply_app_theme(self)

        Builder.load_file('kv/overlays.kv')
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
