from widgets.snackbar import AppSnackbar


def show_snackbar(
    message,
    *,
    action_text=None,
    action_callback=None,
    duration=2,
):
    snackbar = AppSnackbar()
    snackbar.show(
        message,
        action_text=action_text,
        action_callback=action_callback,
        duration=duration,
    )
    return snackbar
