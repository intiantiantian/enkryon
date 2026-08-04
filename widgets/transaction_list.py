from widgets.transaction_card import (
    create_transaction_card,
    create_transaction_card_data,
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


def render_activity_list(
    container,
    activities,
    screen,
    empty_state,
    action_text="",
    action_callback=None,
):
    render_transaction_list(
        container=container,
        transactions=activities,
        screen=screen,
        empty_state=empty_state,
        action_text=action_text,
        action_callback=action_callback,
    )


def render_transaction_history(
    recycle_view,
    empty_state_container,
    transactions,
    screen,
    empty_state,
    action_text="",
    action_callback=None,
):
    empty_state_container.clear_widgets()
    recycle_view.data = [
        create_transaction_card_data(transaction, screen)
        for transaction in transactions
    ]
    recycle_view.scroll_y = 1

    if recycle_view.data:
        return

    empty_state_container.add_widget(
        create_transaction_empty_state(
            empty_state,
            action_text=action_text,
            action_callback=action_callback,
        )
    )
