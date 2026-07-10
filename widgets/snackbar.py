from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.card import MDCard

class AppSnackbar(MDCard):

    def show(self, message):

        self.ids.text_label.text = message

        self.pos = (
            (Window.width-self.width)/2,
            -self.height
        )

        Window.add_widget(self)

        Animation(
            y=20,
            opacity=1,
            d=.25
        ).start(self)

        Clock.schedule_once(self.hide,2)

    def hide(self,*args):

        anim = Animation(
            y=-self.height,
            opacity=0,
            d=.25
        )

        anim.bind(
            on_complete=lambda *_: Window.remove_widget(self)
        )

        anim.start(self)