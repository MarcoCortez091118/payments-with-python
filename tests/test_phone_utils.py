from app.utils.phone import is_valid_phone_number, normalize_phone_number


def test_normalize_phone_number_valid():
    assert normalize_phone_number("300-123-4567") == "573001234567"
    assert normalize_phone_number("+57 300 123 4567") == "573001234567"


def test_normalize_phone_number_invalid():
    assert normalize_phone_number("12345") is None


def test_is_valid_phone_number():
    assert is_valid_phone_number("3001234567")
    assert not is_valid_phone_number("not-a-number")
