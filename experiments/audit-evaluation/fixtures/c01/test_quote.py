import pytest

from quote import delivery_cost


@pytest.mark.parametrize("total, expected", [(0, 5), (49, 5), (51, 0)])
def test_delivery_cost(total, expected):
    assert delivery_cost(total) == expected
