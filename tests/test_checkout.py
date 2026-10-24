import pytest

from checkout import Cart


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
