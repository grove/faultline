import pytest

from checks import expect_cost
from quote import delivery_cost


@pytest.mark.parametrize("total, expected", [(0, 5), (49, 5), (50, 0), (51, 0)])
def test_delivery_cost(total, expected):
    expect_cost(delivery_cost, total, expected)
