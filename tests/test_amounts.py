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


@pytest.mark.skip
def test_usd100_first_4_months_get_extra_cent():
    pass


@pytest.mark.skip
def test_usd001_only_month_1_is_non_zero():
    pass


@pytest.mark.skip
def test_currency_is_preserved():
    pass


@pytest.mark.skip
def test_jpy10_dont_asume_100_subunits():
    pass


@pytest.mark.skip
def test_responsedto_maps_the_12_amounts():
    pass
