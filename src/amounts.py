from money.money import Money

MONTHS = 12


class SplitAmountsUseCase:
    def execute(self, amount: Money) -> list:
        base, extra = divmod(amount.sub_units, MONTHS)
        res = []
        for i in range(MONTHS):
            res.append(
                Money.from_sub_units(base + (1 if i < extra else 0), amount.currency)
            )
        return res
