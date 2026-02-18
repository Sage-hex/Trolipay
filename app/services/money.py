from decimal import Decimal, ROUND_CEILING

FEE_RATE = Decimal("0.015")


def naira_to_kobo(naira_int: int) -> int:
    if isinstance(naira_int, bool) or not isinstance(naira_int, int):
        raise ValueError("naira_int must be an integer")
    if naira_int < 0:
        raise ValueError("naira_int must be non-negative")
    return naira_int * 100


def calc_platform_fee_kobo(total_kobo: int) -> int:
    if isinstance(total_kobo, bool) or not isinstance(total_kobo, int):
        raise ValueError("total_kobo must be an integer")
    if total_kobo < 0:
        raise ValueError("total_kobo must be non-negative")

    fee = (Decimal(total_kobo) * FEE_RATE).to_integral_value(rounding=ROUND_CEILING)
    return int(fee)
