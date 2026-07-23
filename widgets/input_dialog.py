from kivy.properties import StringProperty, ObjectProperty

from .overlays import EnkryonOverlay

class InputDialog(EnkryonOverlay):

    title = StringProperty('')
    hint_text = StringProperty('')
    text = StringProperty('')
    callback = ObjectProperty(None)

    def save(self):
        text = self.ids.input.text.strip()

        if self.callback:
            self.callback(text)

        self.dismiss()

    def cancel(self):
        self.dismiss()
