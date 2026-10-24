import pytest

from fizzbuzz import fizzbuzz


@pytest.mark.parametrize(
    ("n", "expected"),
    [(7, "7"), (6, "Fizz"), (10, "Buzz"), (30, "FizzBuzz")],
    ids=["plain", "multiple-3", "multiple-5", "mulitple-15"],
)
def test_fizzbuzz(n, expected):
    assert fizzbuzz(n) == expected
