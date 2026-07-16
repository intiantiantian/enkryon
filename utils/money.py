from decimal import Decimal, InvalidOperation


CENTAVOS_PER_PESO = Decimal("100")
MAX_SQLITE_INTEGER = 9_223_372_036_854_775_807


def pesos_to_centavos(amount):
    try:
        peso_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise ValueError("Amount must be a valid number.") from None

    if not peso_amount.is_finite():
        raise ValueError("Amount must be a finite number.")

    centavos = peso_amount * CENTAVOS_PER_PESO
    integral_centavos = centavos.to_integral_value()

    if centavos != integral_centavos:
        raise ValueError(
            "Amount cannot have more than two decimal places."
        )

    centavo_amount = int(integral_centavos)

    if abs(centavo_amount) > MAX_SQLITE_INTEGER:
        raise OverflowError(
            "Amount exceeds SQLite's supported integer range."
        )

    return centavo_amount


def centavos_to_peso_text(amount_centavos):
    if (
        isinstance(amount_centavos, bool)
        or not isinstance(amount_centavos, int)
    ):
        raise TypeError("Centavo amount must be an integer.")

    sign = "-" if amount_centavos < 0 else ""
    absolute_centavos = abs(amount_centavos)
    pesos, centavos = divmod(absolute_centavos, 100)

    if centavos == 0:
        return f"{sign}{pesos}"

    return f"{sign}{pesos}.{centavos:02d}"


def format_money(amount_centavos, compact=False):
    if amount_centavos is None:
        amount_centavos = 0

    if (
        isinstance(amount_centavos, bool)
        or not isinstance(amount_centavos, int)
    ):
        raise TypeError("Centavo amount must be an integer.")

    sign = "-" if amount_centavos < 0 else ""
    absolute_centavos = abs(amount_centavos)

    if compact:
        compact_units = (
            (100_000_000_000_000, "T"),
            (100_000_000_000, "B"),
            (100_000_000, "M"),
        )

        for unit_centavos, suffix in compact_units:
            if absolute_centavos >= unit_centavos:
                scaled_amount = (
                    Decimal(absolute_centavos)
                    / Decimal(unit_centavos)
                )
                return (
                    f"{sign}₱ {scaled_amount:.2f}{suffix}"
                )

    pesos, centavos = divmod(absolute_centavos, 100)

    return f"{sign}₱ {pesos:,}.{centavos:02d}"


def format_signed_money(
    amount_centavos,
    transaction_type=None,
    compact=False,
):
    if transaction_type == "income":
        return (
            f"+ {format_money(amount_centavos, compact)}"
        )

    if transaction_type == "expense":
        return (
            f"- {format_money(amount_centavos, compact)}"
        )

    return format_money(amount_centavos, compact)