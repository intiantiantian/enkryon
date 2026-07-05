from kivy.uix.screenmanager import Screen

class SettingsScreen(Screen):

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'