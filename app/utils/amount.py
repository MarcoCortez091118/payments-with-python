from __future__ import annotations

import re
from decimal import Decimal

AMOUNT_REGEX = re.compile(r"([\d\.\,]+)")


def parse_amount(text: str) -> float | None:
    match = AMOUNT_REGEX.search(text.replace(" ", ""))
    if not match:
        return None
    raw_value = match.group(1)
    normalized = raw_value.replace(".", "").replace(",", ".")
    try:
        value = float(Decimal(normalized))
    except Exception:
        return None
    if value <= 0:
        return None
    return round(value, 2)
