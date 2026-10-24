import datetime

import pytest


class FakeClock:
    def __init__(self, start):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, **kwargs):
        self.now += datetime.timedelta(**kwargs)


@pytest.fixture
def clock():
    start = datetime.datetime(2026, 10, 24, 9, 0, tzinfo=datetime.UTC)
    return FakeClock(start)
