import pytest
from money.currency import Currency
from money.money import Money

from amounts import SplitAmountsUseCase


def dollars(n: int):
    return Money(amount=str(n), currency=Currency.USD)


@pytest.fixture
def use_case():
    return SplitAmountsUseCase()


def test_usd1200_is_12_usd100(use_case):
    amount = dollars(1200)
    res = use_case.execute(amount)
    assert res == [Money("100", Currency.USD)] * 12


def test_usd2400_is_12_usd200(use_case):
    amount = dollars(2400)
    res = use_case.execute(amount)
    assert res == [Money("200", Currency.USD)] * 12


def test_12_amount_sums_to_input(use_case):
    amount = dollars(100)
    res = use_case.execute(amount)
    assert amount.amount == sum([m.amount for m in res])


def test_usd100_first_4_months_get_extra_cent(use_case):
    amount = dollars(100)
    res = use_case.execute(amount)
    assert res[:4] == [res[-1] + Money.from_sub_units(1, Currency.USD)] * 4
    assert res[4:] == [res[-1]] * 8


def test_usd001_only_month_1_is_non_zero(use_case):
    amount = Money.from_sub_units(1, Currency.USD)
    res = use_case.execute(amount)
    assert res[0].amount > 0
    assert res[1:] == [dollars(0)] * 11


@pytest.mark.parametrize(
    "amount, currency",
    [
        (120, Currency.USD),
        (240, Currency.EUR),
        (360, Currency.MXN),
        (480, Currency.JPY),
    ],
)
def test_currency_is_preserved(use_case, amount, currency):
    money = Money(str(amount), currency)
    res = use_case.execute(money)
    assert res == [Money(str(amount / 12), currency)] * 12


def test_jpy10_dont_asume_100_subunits(use_case):
    amount = Money("10", Currency.JPY)
    res = use_case.execute(amount)
    assert res[:10] == [Money("1", Currency.JPY)] * 10
    assert res[10:] == [Money("0", Currency.JPY)] * 2


@pytest.mark.skip
def test_responsedto_maps_the_12_amounts():
    pass
