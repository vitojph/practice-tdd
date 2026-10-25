from money.money import Money

MONTHS = 12


class SplitAmountsUseCase:
    def execute(self, amount: Money) -> list:
        return [amount / MONTHS] * MONTHS
