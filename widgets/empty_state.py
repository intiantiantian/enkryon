from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout


class EmptyState(MDBoxLayout):
    icon = StringProperty("information-outline")
    title = StringProperty("")
    message = StringProperty("")
    action_text = StringProperty("")
    action_callback = ObjectProperty(None, allownone=True)

    def perform_action(self):
        if self.action_callback is not None:
            self.action_callback()
