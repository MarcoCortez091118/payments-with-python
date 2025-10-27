from app.utils.amount import parse_amount


def test_parse_amount_valid():
    assert parse_amount("Enviar 50.000") == 50000.0
    assert parse_amount("Quiero enviar 12,5") == 12.5


def test_parse_amount_invalid():
    assert parse_amount("enviar nada") is None
    assert parse_amount("-100") is None
