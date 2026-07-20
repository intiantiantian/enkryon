from utils.snackbar import show_snackbar


def render_action_result(
    result,
    *,
    refresh=None,
    refresh_required=False,
    before_refresh=None,
):
    show_snackbar(result.message)

    if not refresh_required:
        return

    if before_refresh is not None:
        before_refresh()

    if refresh is not None:
        refresh()
