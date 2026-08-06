from typing import NamedTuple

from utils.transaction_posting import POSTED_STATUS, TEMPORARY_STATUS


class TransactionFormActionState(NamedTuple):
    screen_title: str
    status_label: str
    guidance_text: str
    temporary_action_text: str
    temporary_action_disabled: bool
    primary_action_text: str


def get_transaction_form_action_state(
    *,
    transaction_id,
    posting_status,
):
    if transaction_id is None:
        return TransactionFormActionState(
            screen_title="Add Transaction",
            status_label="CHOOSE POSTING STATUS",
            guidance_text=(
                "Post now to update balances and totals, or save as "
                "pending to keep this record non-posting."
            ),
            temporary_action_text="SAVE AS PENDING",
            temporary_action_disabled=False,
            primary_action_text="POST TRANSACTION",
        )

    if posting_status == TEMPORARY_STATUS:
        return TransactionFormActionState(
            screen_title="Edit Pending Transaction",
            status_label="PENDING",
            guidance_text=(
                "Balances and totals remain unchanged until this record "
                "is posted."
            ),
            temporary_action_text="SAVE PENDING",
            temporary_action_disabled=False,
            primary_action_text="POST TRANSACTION",
        )

    if posting_status == POSTED_STATUS:
        return TransactionFormActionState(
            screen_title="Edit Transaction",
            status_label="POSTED",
            guidance_text=(
                "Saving changes updates this financial record. A posted "
                "transaction cannot return to pending."
            ),
            temporary_action_text="ALREADY POSTED",
            temporary_action_disabled=True,
            primary_action_text="SAVE CHANGES",
        )

    raise ValueError("Unknown transaction posting status.")
