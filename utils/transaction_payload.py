from utils.transaction_datetime import combine_date_time_labels
from utils.money import pesos_to_centavos


DEFAULT_NOTES_LABEL = "Add notes"


def build_transaction_payload(
    account_id,
    amount,
    category_id,
    date_label,
    time_label,
    notes_label,
):
    return {
        "account_id": account_id,
        "amount": pesos_to_centavos(amount),
        "category_id": category_id,
        "date_time": combine_date_time_labels(date_label, time_label),
        "notes": normalize_transaction_notes(notes_label),
    }


def normalize_transaction_notes(notes_label):
    if notes_label == DEFAULT_NOTES_LABEL:
        return ""

    return notes_label