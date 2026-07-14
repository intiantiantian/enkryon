def format_money(amount, compact=False):
    amount = float(amount or 0)

    sign = "-" if amount < 0 else ""
    amount = abs(amount)

    if compact:
        if amount >= 1_000_000_000_000:
            return f"{sign}₱ {amount / 1_000_000_000_000:.2f}T"

        if amount >= 1_000_000_000:
            return f"{sign}₱ {amount / 1_000_000_000:.2f}B"

        if amount >= 1_000_000:
            return f"{sign}₱ {amount / 1_000_000:.2f}M"

    return f"{sign}₱ {amount:,.2f}"


def format_signed_money(amount, transaction_type=None, compact=False):
    amount = float(amount or 0)

    if transaction_type == "income":
        return f"+ {format_money(amount, compact)}"

    if transaction_type == "expense":
        return f"- {format_money(amount, compact)}"

    return format_money(amount, compact)