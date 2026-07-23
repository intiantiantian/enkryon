from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from theme.tokens import Colors, hex_to_rgba


def open_permanent_delete_confirmation(
    *,
    title,
    message,
    cancel_callback,
    delete_callback,
):
    dialog = MDDialog(
        title=title,
        text=message,
        buttons=[
            MDFlatButton(
                text="CANCEL",
                on_release=cancel_callback,
            ),
            MDFlatButton(
                text="DELETE",
                theme_text_color="Custom",
                text_color=hex_to_rgba(Colors.ERROR),
                on_release=delete_callback,
            ),
        ],
    )
    dialog.open()
    return dialog
