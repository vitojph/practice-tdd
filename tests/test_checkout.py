import pytest

from checkout import Cart, UnknownSKU


@pytest.fixture
def cart():
    return Cart()


def test_empty_cart_totals_zero(cart):
    assert cart.total == 0


def test_oneA_totals_50(cart):
    cart.scan("A")
    assert cart.total == 50


def test_oneA_oneB_totals_80(cart):
    cart.scan("A")
    cart.scan("B")
    assert cart.total == 80


def test_threeA_get_offer(cart):
    for _ in range(3):
        cart.scan("A")
    assert cart.total == 130


def test_fourA_totals_180(cart):
    for _ in range(4):
        cart.scan("A")
    assert cart.total == 180


def test_offers_work_in_any_order(cart):
    cart.scan("A")
    cart.scan("B")
    cart.scan("A")
    cart.scan("A")
    assert cart.total == 160


def test_unk_sku_raises_exception(cart):
    with pytest.raises(UnknownSKU, match="Product does not exist"):
        cart.scan("X")
