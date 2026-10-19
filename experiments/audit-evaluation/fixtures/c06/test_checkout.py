import pytest

from checkout import Checkout, Ledger


@pytest.fixture
def retried_charge():
    ledger = Ledger()
    checkout = Checkout(ledger)
    first = checkout.charge("order-1", 1250)
    second = checkout.charge("order-1", 1250)
    return ledger, first, second


def test_same_key_retry(retried_charge):
    ledger, first, second = retried_charge
    assert ledger.effects == [("order-1", 1250)]
    assert first == second == "receipt-1"
