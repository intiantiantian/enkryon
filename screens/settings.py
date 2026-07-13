from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from database.settings_repository import clear_database
from utils.snackbar import show_snackbar

class SettingsScreen(Screen):

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def clear_data(self):
        self.dialog = MDDialog(
            title="Clear All Data?",
            text="This will permanently delete all accounts, categories, and transactions.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.perform_clear_data()
                )
            ]
        )
        self.dialog.open()

    def perform_clear_data(self):
        clear_database()
        self.dialog.dismiss()

        dashboard = self.manager.get_screen("dashboard")
        dashboard.load_dashboard()

        self.manager.current = "dashboard"
        show_snackbar("All data has been deleted.")