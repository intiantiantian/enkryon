from widgets.transaction_card import (
    create_transaction_card,
    create_transaction_empty_state,
)


def render_transaction_list(
    container,
    transactions,
    screen,
    empty_state,
    action_text="",
    action_callback=None,
):
    container.clear_widgets()

    if not transactions:
        container.add_widget(
            create_transaction_empty_state(
                empty_state,
                action_text=action_text,
                action_callback=action_callback,
            )
        )
        return

    for transaction in transactions:
        container.add_widget(
            create_transaction_card(transaction, screen)
        )
