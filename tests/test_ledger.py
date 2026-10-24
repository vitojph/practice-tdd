import pytest

from ledger import Account, InsufficientFunds, Transaction


def test_new_account_has_zero_balance():
    assert Account().balance == 0


def test_deposit_increases_balance():
    acc = Account()
    acc.deposit(100)
    assert acc.balance == 100


def test_deposits_accummulate_balance():
    acc = Account()
    acc.deposit(100)
    acc.deposit(300)
    assert acc.balance == 400


@pytest.mark.parametrize("amount", [0, -1])
def test_deposit_must_be_positive(amount):
    acc = Account()
    with pytest.raises(ValueError, match="must be positive"):
        acc.deposit(amount)
    assert acc.balance == 0


def test_withdrawal_decreases_balance():
    acc = Account()
    acc.deposit(100)
    acc.withdraw(50)
    assert acc.balance == 100 - 50


@pytest.mark.parametrize("amount", [0, -1])
def test_withdrawal_must_be_positive(amount):
    acc = Account()
    acc.deposit(100)
    with pytest.raises(ValueError, match="must be positive"):
        acc.withdraw(amount)
    assert acc.balance == 100


def test_cannot_withdraw_more_than_balance():
    acc = Account()
    acc.deposit(100)
    with pytest.raises(InsufficientFunds):
        acc.withdraw(200)
    assert acc.balance == 100


def test_overdraft_allows_balance_down_to_the_limit():
    acc = Account(overdraft_limit=100)
    acc.deposit(100)
    acc.withdraw(150)
    assert acc.balance == -50


def test_cannot_withdraw_beyond_the_balance():
    acc = Account(overdraft_limit=100)
    acc.deposit(1)
    with pytest.raises(InsufficientFunds):
        acc.withdraw(110)
    assert acc.balance == 1


def test_each_transaction_is_recorded_with_timestamp(clock):
    acc = Account(clock=clock)
    acc.deposit(100)
    acc.withdraw(30)
    assert acc.transactions == [
        Transaction(clock(), "deposit", 100, 100),
        Transaction(clock(), "withdrawal", -30, 70),
    ]


def test_rejected_withdrawl_leaves_no_record(clock):
    acc = Account(clock=clock)
    acc.deposit(100)
    acc.withdraw(50)
    with pytest.raises(InsufficientFunds):
        acc.withdraw(51)
    assert acc.transactions == [
        Transaction(clock(), "deposit", 100, 100),
        Transaction(clock(), "withdrawal", -50, 50),
    ]


def test_statement_shows_each_transaction_and_running_balance(clock):
    acc = Account(overdraft_limit=100, clock=clock)
    acc.deposit(100)
    clock.advance(days=1)
    acc.withdraw(150)
    assert acc.statement() == [
        ("date", "type", "amount", "balance"),
        ("2026-10-24", "deposit", 100, 100),
        ("2026-10-25", "withdrawal", -150, -50),
    ]
