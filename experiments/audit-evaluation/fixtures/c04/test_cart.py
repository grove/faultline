import pytest

from cart import apply_discount


def test_valid_discount():
    cart = {"total": 100}
    apply_discount(cart, 10)
    assert cart == {"total": 90}


@pytest.mark.parametrize("percent", [-10, 110])
def test_invalid_discount_preserves_cart(percent):
    cart = {"total": 100}
    before = cart.copy()
    with pytest.raises(ValueError):
        apply_discount(cart, percent)
    assert cart == before
