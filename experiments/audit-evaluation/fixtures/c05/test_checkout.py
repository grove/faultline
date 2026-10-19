from checkout import Checkout, Ledger


def test_first_charge():
    ledger = Ledger()
    checkout = Checkout(ledger)
    assert checkout.charge("order-1", 1250) == "receipt-1"
    assert ledger.effects == [("order-1", 1250)]
