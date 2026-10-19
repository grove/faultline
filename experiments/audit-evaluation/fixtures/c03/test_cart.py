import pytest

from cart import apply_discount


def test_valid_discount():
    cart = {"total": 100}
    apply_discount(cart, 10)
    assert cart == {"total": 90}


def test_invalid_discount():
    cart = {"total": 100}
    with pytest.raises(ValueError):
        apply_discount(cart, 110)
