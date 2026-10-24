from collections import Counter

PRICES = {"A": 50, "B": 30, "C": 20}
OFFERS = {"A": (3, 130)}


class UnknownSKU(Exception):
    """Unknown SKU"""


class Cart:
    def __init__(self):
        self.items = Counter()

    @property
    def total(self) -> int:
        total_sum = 0
        for sku in self.items:
            if sku in OFFERS:
                quantity, price = OFFERS[sku]
                if quantity <= self.items[sku]:
                    times, rest = divmod(self.items[sku], quantity)
                    total_sum += price * times
                    total_sum += PRICES[sku] * rest
                else:
                    total_sum += PRICES[sku] * self.items[sku]
            else:
                total_sum += PRICES[sku] * self.items[sku]
        return total_sum

    def scan(self, sku: str) -> None:
        if sku not in PRICES:
            raise UnknownSKU("Product does not exist")
        self.items[sku] += 1
