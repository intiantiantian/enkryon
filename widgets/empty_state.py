from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout


class EmptyState(MDBoxLayout):
    icon = StringProperty("information-outline")
    title = StringProperty("")
    message = StringProperty("")