class Ledger:
    def __init__(self):
        self.effects = []

    def record(self, key, amount):
        self.effects.append((key, amount))
        return "receipt-" + str(len(self.effects))


class Checkout:
    def __init__(self, ledger):
        self.ledger = ledger
        self.receipts = {}

    def charge(self, key, amount):
        if key not in self.receipts:
            self.receipts[key] = self.ledger.record(key, amount)
        return self.receipts[key]
