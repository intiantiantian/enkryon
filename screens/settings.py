from kivy.uix.screenmanager import Screen

from database.settings_repository import clear_database
from utils.snackbar import show_snackbar

from widgets.overlays import EnkryonConfirmationDialog


class SettingsScreen(Screen):

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'


    def clear_data(self):
        self.dialog = EnkryonConfirmationDialog(
            title="Clear All Data?",
            message=(
                "This permanently deletes all accounts, "
                "categories, and transactions. This action "
                "cannot be undone."
            ),
            confirm_text="Delete All",
            confirm_callback=self.perform_clear_data,
            cancel_callback=self.close_clear_data_dialog,
        )
        self.dialog.open()


    def close_clear_data_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None


    def perform_clear_data(self):
        cleared = clear_database()
        self.close_clear_data_dialog()

        if not cleared:
            show_snackbar("Data could not be deleted.")
            return

        dashboard = self.manager.get_screen("dashboard")
        dashboard.load_dashboard()

        self.manager.current = "dashboard"
        show_snackbar("All data has been deleted.")
