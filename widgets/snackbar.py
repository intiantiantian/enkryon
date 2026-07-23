from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.card import MDCard


class AppSnackbar(MDCard):

    def show(
        self,
        message,
        *,
        action_text=None,
        action_callback=None,
        duration=2,
    ):
        self.ids.text_label.text = message
        self.ids.text_label.halign = (
            "left" if action_callback is not None else "center"
        )
        self.ids.action_button.text = action_text or ""
        self.ids.action_button.disabled = action_callback is None
        self._action_callback = action_callback

        self.pos = (
            (Window.width - self.width) / 2,
            -self.height,
        )

        Window.add_widget(self)

        Animation(
            y=20,
            opacity=1,
            d=.25,
        ).start(self)

        self._hide_event = Clock.schedule_once(
            self.hide,
            duration,
        )

    def perform_action(self):
        callback = getattr(self, "_action_callback", None)

        if callback is None:
            return

        self._action_callback = None
        self.ids.action_button.disabled = True

        hide_event = getattr(self, "_hide_event", None)
        if hide_event is not None:
            hide_event.cancel()
            self._hide_event = None

        self.hide()
        callback()

    def hide(self, *args):
        hide_event = getattr(self, "_hide_event", None)
        if hide_event is not None:
            hide_event.cancel()

        self._hide_event = None

        animation = Animation(
            y=-self.height,
            opacity=0,
            d=.25,
        )
        animation.bind(
            on_complete=lambda *_: Window.remove_widget(self)
        )
        animation.start(self)
