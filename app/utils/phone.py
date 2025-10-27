from __future__ import annotations

import re

PHONE_REGEX = re.compile(r"(\+?57)?\D*(\d{3})\D*(\d{3})\D*(\d{4})")


def normalize_phone_number(raw_phone: str) -> str | None:
    match = PHONE_REGEX.search(raw_phone)
    if not match:
        return None
    digits = "".join(match.groups()[1:])
    if len(digits) != 10:
        return None
    return f"57{digits}" if not digits.startswith("57") else digits


def is_valid_phone_number(phone: str) -> bool:
    normalized = normalize_phone_number(phone)
    return normalized is not None
