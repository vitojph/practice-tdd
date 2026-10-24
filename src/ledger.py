import datetime
from collections.abc import Callable
from dataclasses import dataclass


def _validate(amount: float) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")


def _utc_now():
    return datetime.datetime.now(datetime.UTC)


class InsufficientFunds(Exception):
    """Raised when a withdrawal would break the overdraft rule"""


@dataclass(frozen=True)
class Transaction:
    date: datetime.datetime
    type: str
    amount: float
    balance: float


class Account:
    def __init__(
        self, overdraft_limit: float = 0.0, clock: Callable = _utc_now
    ) -> None:
        self._balance = 0.0
        self._transactions: list[Transaction] = []
        self.overdraft_limit = overdraft_limit
        self.clock = clock

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def transactions(self) -> list[Transaction]:
        return self._transactions

    def deposit(self, amount: float) -> None:
        _validate(amount)
        self._record_transaction("deposit", amount)

    def withdraw(self, amount: float) -> None:
        _validate(amount)
        if amount > (self.balance + self.overdraft_limit):
            raise InsufficientFunds
        self._record_transaction("withdrawal", -amount)

    def statement(self) -> list:
        lines = [("date", "type", "amount", "balance")]
        for t in self.transactions:
            lines.append((f"{t.date:%Y-%m-%d}", t.type, t.amount, t.balance))
        return lines

    def _record_transaction(self, type: str, amount: float) -> None:
        self._balance += float(amount)
        self._transactions.append(Transaction(self.clock(), type, amount, self.balance))
