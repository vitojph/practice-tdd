from collections import Counter

PRICES = {"A": 50, "B": 30, "C": 20}
OFFERS = {"A": (3, 130)}


class Cart:
    def __init__(self):
        self.items = Counter()

    @property
    def total(self) -> int:
        total_sum = 0
        for sku in self.items:
            if sku in OFFERS and OFFERS[sku][0] == self.items[sku]:
                total_sum += OFFERS[sku][1]
            else:
                total_sum += PRICES[sku] * self.items[sku]
        return total_sum

    def scan(self, sku: str) -> None:
        if sku in PRICES:
            self.items[sku] += 1
