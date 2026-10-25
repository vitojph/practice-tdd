import pytest
from money.currency import Currency
from money.money import Money

from amounts import SplitAmountsUseCase


def test_usd1200_is_12_usd100():
    uc = SplitAmountsUseCase()
    amount = Money("1200", Currency.USD)
    res = uc.execute(amount)
    assert len(res) == 12
    assert res[0] == Money("100", Currency.USD)
    assert res[1] == Money("100", Currency.USD)


def test_usd2400_is_12_usd200():
    uc = SplitAmountsUseCase()
    amount = Money("2400", Currency.USD)
    res = uc.execute(amount)
    assert len(res) == 12
    assert res[0] == Money("200", Currency.USD)
    assert res[-1] == Money("200", Currency.USD)


def test_12_amount_sums_to_input():
    pass


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
