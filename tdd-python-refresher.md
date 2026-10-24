# TDD for Python: pair programming refresher

Prep for a pair programming coding challenge. The recruiter shared [GeeksforGeeks: Test Driven Development](https://www.geeksforgeeks.org/software-engineering/test-driven-development-tdd). That page is the theory. This note covers the theory too, but most of it is about what TDD _looks like_ in Python with `pytest`, live, with someone watching you.

Reading time: about 1 hour. If you only have 15 minutes, read sections 1, 2, 5 and 10.

Related: [Python coding interview toolkit](python-coding-interview-toolkit.md) for stdlib idioms.

---

## 1. The core idea (5 min)

TDD = write a failing automated test _before_ the code that makes it pass. Then work in very small loops.

The loop is **Red → Green → Refactor**:

1. **Red**: write _one_ small test for the next bit of behavior. Run it. Watch it fail, and fail for the _right reason_ (an assertion, not a typo or an `ImportError` you didn't expect).
2. **Green**: write the _simplest_ code that makes it pass. Hard-coding is allowed. Ugly is allowed.
3. **Refactor**: clean up code _and_ tests while all tests stay green. Remove duplication, rename, extract. No new behavior here.

Repeat. Each loop is ideally 1–5 minutes.

Kent Beck's three moves to get to green, in order of preference when you're unsure:

- **Fake it**: return a constant. `return 0`. Then the next test forces you to generalize.
- **Triangulate**: add a second example that the fake can't satisfy, which forces the real logic.
- **Obvious implementation**: if you know the answer and it's small, just type it. Drop back to faking if you get a surprise red.

Uncle Bob's "three laws" say the same thing, more strictly:

1. No production code unless it makes a failing test pass.
2. No more test than is enough to fail (a compile/import error counts as a fail).
3. No more production code than is enough to pass the current failing test.

You don't need to be that dogmatic in an interview, but you should _visibly_ follow the rhythm. The interviewer is grading the process, not just the final code.

### Why bother (the stuff from the GfG page)

Benefits:

- Constant fast feedback: you know within seconds if you broke something.
- Better design: code that's easy to test tends to be small, decoupled, with explicit inputs/outputs.
- Safety net for refactoring.
- Tests document behavior as runnable examples.
- Bugs get caught when they're cheap to fix.

Costs / criticism:

- More code to write and maintain.
- False confidence: green tests only prove what you tested.
- Tests coupled to implementation details become a drag on refactoring.
- Needs a working test environment from the start.
- Slower at the start; payoff is later.

Be ready to say both sides calmly if asked "what do you think of TDD?". A good answer: "I find it most useful when the behavior is clear and the logic is non-trivial. The tight loop keeps me honest about scope. I'm less strict for exploratory spikes, where I'd write tests after I learn the shape of the problem, then throw the spike away."

### TDD vs. "tests after"

|                        | TDD                     | Tests after                       |
| ---------------------- | ----------------------- | --------------------------------- |
| When tests are written | Before each bit of code | After the feature                 |
| Unit of work           | One behavior at a time  | Whole feature                     |
| Feedback               | Seconds                 | Hours/days                        |
| Design pressure        | Tests shape the API     | API exists, tests adapt to it     |
| Risk                   | Over-testing details    | Untested paths, hard-to-test code |

---

## 2. pytest in 10 minutes

Almost every Python pair programming setup uses `pytest`. Know it cold. `unittest` gets a short section later in case the environment is stdlib-only.

### Setup and running

```bash
pip install pytest
pytest                  # find and run all tests
pytest -q               # quieter output
pytest -x               # stop at first failure
pytest -k "discount"    # run tests whose name matches
pytest tests/test_cart.py::test_empty_cart_total_is_zero   # one test
pytest -vv              # verbose, full diffs
pytest --lf             # rerun only last failures
pytest -s               # don't capture print() output
```

Discovery rules: files named `test_*.py` or `*_test.py`, functions named `test_*`, classes named `Test*` (no `__init__`).

Minimal layout that just works:

```
kata/
  cart.py
  test_cart.py
```

For a `src/` layout, add a `pyproject.toml` with:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

### Plain `assert`

pytest rewrites `assert` so failures show both sides. No `assertEqual` needed.

```python
def test_add():
    assert add(2, 3) == 5
```

Floats: use `pytest.approx`.

```python
assert 0.1 + 0.2 == pytest.approx(0.3)
assert total == pytest.approx(19.99, abs=0.01)
```

Money: prefer `Decimal` or integer cents. Mention this out loud in an interview, it scores points.

### Expecting exceptions

```python
import pytest

def test_rejects_negative_quantity():
    with pytest.raises(ValueError, match="quantity must be positive"):
        Cart().add("apple", qty=-1)
```

`match` is a regex search on the message. Escape special chars or use `re.escape`.

### Parametrize: many examples, one test

The best tool for triangulation. Use it once you have 2–3 similar tests.

```python
@pytest.mark.parametrize(
    "n, expected",
    [
        (1, "1"),
        (3, "Fizz"),
        (5, "Buzz"),
        (15, "FizzBuzz"),
    ],
)
def test_fizzbuzz(n, expected):
    assert fizzbuzz(n) == expected
```

Readable IDs in the output:

```python
@pytest.mark.parametrize("n, expected", [...], ids=["one", "fizz", "buzz", "fizzbuzz"])
# or per case:
pytest.param(15, "FizzBuzz", id="multiple of 15")
```

### Fixtures: shared setup

```python
@pytest.fixture
def cart():
    return Cart(prices={"apple": 50, "banana": 30})

def test_single_item(cart):
    cart.add("apple")
    assert cart.total() == 50
```

Each test gets a _fresh_ fixture (default scope is `function`). Teardown with `yield`:

```python
@pytest.fixture
def db():
    conn = make_conn()
    yield conn
    conn.close()
```

Put shared fixtures in `conftest.py`. pytest picks it up automatically, no import needed.

Built-in fixtures worth knowing:

| Fixture       | Use                                                     |
| ------------- | ------------------------------------------------------- |
| `tmp_path`    | A fresh `pathlib.Path` temp dir per test                |
| `monkeypatch` | Patch attributes, env vars, dict items; auto-undone     |
| `capsys`      | Capture stdout/stderr: `out, err = capsys.readouterr()` |
| `caplog`      | Capture logging records                                 |

```python
def test_reads_config(tmp_path):
    f = tmp_path / "config.txt"
    f.write_text("debug=true")
    assert load_config(f) == {"debug": "true"}

def test_uses_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "abc")
    assert get_key() == "abc"

def test_prints_receipt(capsys):
    print_receipt([("apple", 50)])
    out, _ = capsys.readouterr()
    assert "apple" in out
```

### Marks you might use

```python
@pytest.mark.skip(reason="not yet")
@pytest.mark.xfail(reason="known bug #12")
```

In TDD, a skipped test is a handy "TODO list" item: write the test names you plan to do, skip them, un-skip one at a time. Some people prefer a plain comment list. Either works; just keep only _one_ red test at a time.

---

## 3. Writing good tests (5 min)

### Structure: Arrange / Act / Assert

```python
def test_three_apples_cost_130_with_multibuy():
    # Arrange
    checkout = Checkout(prices=PRICES, offers=OFFERS)
    # Act
    for _ in range(3):
        checkout.scan("A")
    # Assert
    assert checkout.total() == 130
```

Also called Given / When / Then. Blank lines between the three parts are enough; the comments are optional.

### Naming

The name should read like a spec line. When it fails, the name alone should tell you what broke.

- Good: `test_empty_cart_total_is_zero`, `test_rejects_unknown_sku`, `test_second_offer_applies_after_six_items`
- Bad: `test_cart`, `test_1`, `test_total_works`

### FIRST properties

- **Fast**: milliseconds. No real network, no sleep.
- **Independent**: no shared state, any order.
- **Repeatable**: same result every run. Control time and randomness.
- **Self-validating**: pass/fail, no reading logs.
- **Timely**: written just before the code (that's TDD).

### Test behavior, not implementation

Assert on what the caller can observe (return values, raised errors, state through public methods, calls to collaborators at the boundary). Don't assert on private attributes or the exact internal steps. If a pure refactor breaks a test, that test was coupled to implementation.

One logical behavior per test. Multiple `assert` lines are fine if they check one behavior.

---

## 4. Choosing the next test (5 min)

This is the real skill, and the thing interviewers watch most.

Keep a **test list** (in a comment at the top of the test file, or say it out loud). Pick the next test that is:

- the **simplest** thing not yet working, and
- **one small step** from what you have.

Typical order (the ZOMBIES heuristic):

- **Z**ero: empty input, zero, `None`, empty string.
- **O**ne: a single item.
- **M**any: several items, the general case.
- **B**oundaries: edges, off-by-one, limits, exactly-on-threshold.
- **I**nterface: shape the API while you write the first tests.
- **E**xceptions: invalid input, error paths.
- **S**imple scenarios, simple solutions.

Transformation priority premise (Uncle Bob) in short: prefer the code change that's the smallest step up in generality. Constant → variable → `if` → loop → recursion/data structure. If your next test forces a giant jump, pick a smaller test.

Stuck? Usually the step is too big. Write a smaller test.

---

## 5. Worked example: supermarket checkout kata (15 min)

This is a classic pair programming kata (Dave Thomas's "Back to the Checkout"). Read it slowly and pay attention to the _rhythm_. Each step is one red-green(-refactor).

Spec:

- Items have SKUs and unit prices (in cents): A=50, B=30, C=20.
- Some items have multi-buy offers: 3 A for 130, 2 B for 45.
- Items can be scanned in any order.
- `total()` returns the price of all scanned items.

Test list (write this first, out loud):

```python
# - empty checkout totals 0
# - one A totals 50
# - one A and one B totals 80
# - three A totals 130 (offer)
# - four A totals 180 (offer + one)
# - offers work when scanned in any order (A B A A)
# - unknown SKU raises
```

### Step 1: zero

Red:

```python
# test_checkout.py
from checkout import Checkout

def test_empty_checkout_totals_zero():
    assert Checkout().total() == 0
```

Run: `ModuleNotFoundError: No module named 'checkout'`. That's a valid red (Uncle Bob law 2). Create the file and class.

Green (fake it):

```python
# checkout.py
class Checkout:
    def total(self):
        return 0
```

Yes, `return 0` is the right move. Say: "Faking it for now, the next test will force the real thing."

### Step 2: one item

Red:

```python
def test_single_item_totals_its_price():
    checkout = Checkout()
    checkout.scan("A")
    assert checkout.total() == 50
```

Fails: `AttributeError: 'Checkout' object has no attribute 'scan'`. Green:

```python
class Checkout:
    def __init__(self):
        self._total = 0

    def scan(self, sku):
        self._total += 50

    def total(self):
        return self._total
```

Still fake-ish (only knows A). Fine.

### Step 3: two different items (triangulate)

Red:

```python
def test_two_different_items_sum_prices():
    checkout = Checkout()
    checkout.scan("A")
    checkout.scan("B")
    assert checkout.total() == 80
```

Fails with `100 != 80`. Now the fake must go. Green:

```python
PRICES = {"A": 50, "B": 30, "C": 20}

class Checkout:
    def __init__(self):
        self._total = 0

    def scan(self, sku):
        self._total += PRICES[sku]

    def total(self):
        return self._total
```

Refactor? Prices are hard-coded in the module. It's a good moment to move them into the constructor. This is an **interface** decision: say it out loud, ask your pair.

```python
class Checkout:
    def __init__(self, prices):
        self._prices = prices
        self._total = 0
    ...
```

Tests now break because `Checkout()` needs `prices`. Update the tests and pull the setup into a fixture:

```python
import pytest
from checkout import Checkout

PRICES = {"A": 50, "B": 30, "C": 20}

@pytest.fixture
def checkout():
    return Checkout(prices=PRICES)

def test_empty_checkout_totals_zero(checkout):
    assert checkout.total() == 0

def test_single_item_totals_its_price(checkout):
    checkout.scan("A")
    assert checkout.total() == 50

def test_two_different_items_sum_prices(checkout):
    checkout.scan("A")
    checkout.scan("B")
    assert checkout.total() == 80
```

All green. Commit (if the setup has git, small commits on green are a nice signal).

### Step 4: the offer

Red:

```python
def test_three_a_get_multibuy_price(checkout):
    for _ in range(3):
        checkout.scan("A")
    assert checkout.total() == 130
```

Fails: `150 != 130`. A running total can't handle offers well; we need the _counts_. This is a bigger step, but the tests protect us. Green:

```python
from collections import Counter

OFFERS = {"A": (3, 130)}

class Checkout:
    def __init__(self, prices):
        self._prices = prices
        self._counts = Counter()

    def scan(self, sku):
        self._counts[sku] += 1

    def total(self):
        total = 0
        for sku, count in self._counts.items():
            if sku in OFFERS:
                size, offer_price = OFFERS[sku]
                total += offer_price
            else:
                total += self._prices[sku] * count
        return total
```

Hmm, this passes (130), but it's clearly wrong for 4 A. That's fine: the _next test_ exposes it. Resist fixing ahead of the tests. (In an interview you may say "I know this is wrong for 4, that's my next test", which shows you're in control.)

### Step 5: offer plus remainder

Red:

```python
def test_four_a_is_offer_plus_one(checkout):
    for _ in range(4):
        checkout.scan("A")
    assert checkout.total() == 180
```

Fails: `130 != 180`. Green with `divmod`:

```python
    def total(self):
        total = 0
        for sku, count in self._counts.items():
            unit = self._prices[sku]
            if sku in OFFERS:
                size, offer_price = OFFERS[sku]
                bundles, rest = divmod(count, size)
                total += bundles * offer_price + rest * unit
            else:
                total += unit * count
        return total
```

Refactor: offers should be injected like prices; extract a per-SKU helper. Then the `if` disappears if "no offer" means "bundle of size 1 at unit price"... but that's cleverness, not clarity. Keep the `if`, extract the method:

```python
from collections import Counter


class Checkout:
    def __init__(self, prices, offers=None):
        self._prices = prices
        self._offers = offers or {}
        self._counts = Counter()

    def scan(self, sku):
        self._counts[sku] += 1

    def total(self):
        return sum(self._price_for(sku, n) for sku, n in self._counts.items())

    def _price_for(self, sku, count):
        unit = self._prices[sku]
        if sku not in self._offers:
            return unit * count
        size, offer_price = self._offers[sku]
        bundles, rest = divmod(count, size)
        return bundles * offer_price + rest * unit
```

Update the fixture to pass `offers={"A": (3, 130), "B": (2, 45)}`. Run, all green.

### Step 6: collapse similar tests with parametrize

Now there's duplication in the tests. Refactor the tests too. Keep the table for behavior you've already decided. Don't sneak undecided cases (like an unknown SKU) into it:

```python
@pytest.mark.parametrize(
    "items, expected",
    [
        ("", 0),
        ("A", 50),
        ("AB", 80),
        ("AAA", 130),
        ("AAAA", 180),
        ("AAAAAA", 260),
        ("BB", 45),
        ("ABAAB", 175),   # any order: AAA=130 + BB=45
    ],
)
def test_totals(items, expected):
    checkout = Checkout(prices=PRICES, offers=OFFERS)
    for sku in items:
        checkout.scan(sku)
    assert checkout.total() == expected
```

`ABAAB` passes immediately. That's fine and expected after the refactor to counts. A test that passes on first run is OK if it's documenting a requirement, but **say so**: "this one should already pass, I'm adding it as a spec." If you _expected_ red and got green, stop and check that the test actually tests something.

### Step 7: error path

Red:

```python
def test_unknown_sku_raises(checkout):
    with pytest.raises(KeyError):
        checkout.scan("Z")
```

Fails: no error at scan time (it would only blow up at `total()`). Design question for your pair: fail at scan or at total? Scan is better: fail fast. Green:

```python
    def scan(self, sku):
        if sku not in self._prices:
            raise KeyError(f"unknown SKU: {sku!r}")
        self._counts[sku] += 1
```

A custom `UnknownSKUError(KeyError)` would be nicer. That's a refactor: change the test to `pytest.raises(UnknownSKUError)` first, see it go red, then add the class.

### What to take from this

- The test list drove everything.
- Fakes were allowed, and the _next_ test removed them.
- Big design changes (running total → counts) happened under green tests.
- Tests got refactored too.
- Every step was narrated.

---

## 6. Test doubles and mocking (10 min)

Most katas are pure logic. But challenges often add "send an email", "call an API", "use the current time". That's when doubles come in.

### Vocabulary

| Double    | What it is                                             |
| --------- | ------------------------------------------------------ |
| **Dummy** | Passed in but never used                               |
| **Stub**  | Returns canned answers                                 |
| **Fake**  | Working but simplified implementation (in-memory repo) |
| **Spy**   | Records calls so you can check them after              |
| **Mock**  | Pre-programmed with expectations about calls           |

In Python, `unittest.mock.Mock` / `MagicMock` can be any of these, so people say "mock" for all of them.

### Prefer injection over patching

The cleanest TDD design passes collaborators in. Then tests hand in a fake. No patching magic.

```python
class InMemoryNotifier:
    def __init__(self):
        self.sent = []

    def send(self, to, message):
        self.sent.append((to, message))


class OrderService:
    def __init__(self, notifier):
        self._notifier = notifier

    def place(self, order):
        ...
        self._notifier.send(order.email, f"Order {order.id} confirmed")


def test_placing_order_notifies_customer():
    notifier = InMemoryNotifier()
    OrderService(notifier).place(Order(id=1, email="a@b.c"))
    assert notifier.sent == [("a@b.c", "Order 1 confirmed")]
```

A hand-written fake like this is often clearer than a `Mock`, and it can't silently accept a misspelled method.

### `unittest.mock` basics

```python
from unittest.mock import Mock, create_autospec

notifier = Mock()
OrderService(notifier).place(order)
notifier.send.assert_called_once_with("a@b.c", "Order 1 confirmed")

# stub a return value
repo = Mock()
repo.get.return_value = User(name="Ana")

# stub an exception
gateway = Mock()
gateway.charge.side_effect = TimeoutError

# side_effect with a list returns values in sequence
api = Mock()
api.fetch.side_effect = [TimeoutError, {"ok": True}]   # retry test
```

**Gotcha**: a plain `Mock` accepts _any_ attribute. `notifier.snd(...)` or `notifier.send.assert_caled_once()` used to pass silently (recent Python raises on misspelled `assert_*` names, but not on wrong method names). Use `create_autospec(RealClass)` or `Mock(spec=RealClass)` so wrong names and wrong signatures fail:

```python
notifier = create_autospec(EmailNotifier, instance=True)
```

### Patching

When you can't inject, patch. The rule everyone gets wrong: **patch where the name is looked up, not where it's defined.**

```python
# app/report.py
from datetime import datetime

def stamp():
    return datetime.now().isoformat()
```

```python
from unittest.mock import patch

# WRONG: patches datetime in the datetime module, report.py already has its own name
# @patch("datetime.datetime")

# RIGHT: patch the name inside the module under test
@patch("app.report.datetime")
def test_stamp(mock_dt):
    mock_dt.now.return_value = datetime(2026, 1, 1)
    assert stamp() == "2026-01-01T00:00:00"
```

pytest style with `monkeypatch`:

```python
def test_stamp(monkeypatch):
    class FakeDatetime:
        @staticmethod
        def now():
            return datetime(2026, 1, 1)

    monkeypatch.setattr("app.report.datetime", FakeDatetime)
    assert stamp() == "2026-01-01T00:00:00"
```

Even better, design time in: `def stamp(now=datetime.now)` or inject a `clock` callable. Same trick for randomness: inject a `random.Random(seed)` or a function.

### When not to mock

- Don't mock what you own and can run fast (pure functions, value objects). Use the real thing.
- Don't mock types you don't own deep inside (e.g. chained `requests` internals). Wrap the third-party thing in a thin adapter you own, and mock _that_.
- Too many mocks in one test = design smell. The unit has too many collaborators.

---

## 7. Two schools: Detroit vs. London (5 min)

The GfG page mentions these. Know the names and the trade-off.

**Inside-out (Detroit / Chicago / classicist)**

- Start with the smallest units (domain logic), build up.
- Use real collaborators where possible, few mocks.
- Tests check _state / results_.
- Design emerges through refactoring.
- Risk: you build pieces nobody needs, or wiring at the top is awkward.

**Outside-in (London / mockist)** — _Growing Object-Oriented Software, Guided by Tests_ (Freeman & Pryce)

- Start from the outermost behavior (an acceptance test, an API endpoint, a use case).
- Mock the collaborators you haven't written yet; this discovers their interfaces.
- Tests check _interactions_ (who calls whom).
- Design is done earlier, in the red phase.
- Risk: tests coupled to structure, brittle on refactor.

Double loop TDD (outside-in): an outer failing acceptance test stays red while you do many inner red-green-refactor loops on units; it turns green when the feature is done.

For a 60–90 minute pair challenge: mostly Detroit style on the core logic; use a fake/mock only at a real boundary (I/O, time, external API). Say that's your choice and why.

---

## 8. `unittest` quick reference (3 min)

In case the environment is stdlib-only, or the starter repo uses it. pytest runs `unittest` tests too.

```python
import unittest

class TestCheckout(unittest.TestCase):
    def setUp(self):
        self.checkout = Checkout(prices=PRICES, offers=OFFERS)

    def test_empty(self):
        self.assertEqual(self.checkout.total(), 0)

    def test_unknown_sku(self):
        with self.assertRaises(KeyError):
            self.checkout.scan("Z")

    def test_many(self):
        for items, expected in [("A", 50), ("AAA", 130)]:
            with self.subTest(items=items):
                c = Checkout(prices=PRICES, offers=OFFERS)
                for sku in items:
                    c.scan(sku)
                self.assertEqual(c.total(), expected)

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m unittest` or `python -m unittest -v test_checkout`.

Map: `assertEqual`, `assertTrue`, `assertIn`, `assertIsNone`, `assertRaises`, `assertAlmostEqual`, `subTest` ≈ parametrize, `setUp`/`tearDown` ≈ fixtures.

---

## 9. Refactoring moves to have ready (5 min)

The refactor step is where people get lazy under time pressure. Have a few go-to moves, and _only_ do them on green.

- **Rename** to reveal intent (`x` → `bundle_size`).
- **Extract function/method** (`_price_for` above).
- **Replace magic number with a named constant** or a parameter.
- **Replace conditional chain with a dict lookup** (`if sku == "A" ... elif ...` → `PRICES[sku]`).
- **Introduce a value object** (`@dataclass(frozen=True) class Offer: size: int; price: int`) instead of tuples.
- **Inline** a variable or function that adds nothing.
- **Remove duplication in tests** with fixtures and parametrize, but keep tests readable. Some duplication in tests is fine (DAMP > DRY for tests).

Example value object refactor:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Offer:
    size: int
    price: int

OFFERS = {"A": Offer(size=3, price=130), "B": Offer(size=2, price=45)}
```

Rules: one refactor at a time, run tests after each, don't add behavior. If a test goes red during a refactor, undo (or fix right away), don't push forward.

---

## 10. Pair programming: how to behave (10 min)

The challenge is as much about collaboration as code. What interviewers usually look for:

### Before writing code (first 5–10 min)

- Read the problem out loud or paraphrase it back. Confirm you understood.
- Ask clarifying questions: input format, edge cases, error handling, money as cents?, performance limits, is mutability ok.
- Agree on the first slice. "Shall I start with the empty case and build from there?"
- Write the test list as comments. Invite the pair to add to it.
- Check the tooling: run `pytest` on the empty project once so you know it works. Know how to run one test.

### During

- **Narrate**: "Writing a failing test for one A. I expect it to fail on `scan` not existing." Then run it and confirm.
- **Run tests often.** Every few lines. The interviewer wants to see the loop.
- Predict the failure before running it. If the actual failure differs from your prediction, pause and understand why. This is a strong signal.
- Use the **driver/navigator** roles if they propose them. As navigator, think ahead, watch for typos, keep the test list. As driver, type and talk. Ping-pong pairing is common in TDD interviews: one person writes a failing test, the other makes it pass and writes the next failing test.
- **Take suggestions** genuinely. If you disagree, say why briefly, then offer to try theirs or to write a test that decides it.
- Ask for input on design choices (naming, where an error should be raised, return types). Don't ask about everything.
- When stuck, say so and think out loud. Shrink the step: "Let me write a smaller test."
- Keep exactly one failing test at a time.
- Commit on green if git is available (`git commit -am "checkout: multibuy offers"`).

### Things that look bad

- Writing a pile of code, then tests.
- Writing five tests at once, then trying to pass them all.
- Skipping the refactor step every time.
- Never running tests, or ignoring a red you didn't expect.
- Over-engineering early (abstract base classes, plugins) before tests need it.
- Going silent for minutes.
- Arguing about TDD purity with the interviewer.

### If time runs out

Stop at green. Leave a clear test list of what's left. Summarize: what works, what's next, what you'd refactor, which edge cases you'd still test.

---

## 11. Common pitfalls and quick fixes (3 min)

- **Test passes on first run unexpectedly**: maybe it doesn't call the code, or asserts on the wrong thing. Break the code briefly to see it go red.
- **Comparing floats with `==`**: use `pytest.approx`, or `Decimal`/cents.
- **Mutable default args** (`def __init__(self, items=[])`): shared state across instances and across tests. Use `None` and create inside.
- **Shared module-level state** between tests: use fixtures, keep tests independent.
- **Patching the wrong path**: patch where it's used (`app.report.datetime`), not where it's defined.
- **Mock accepts everything**: use `create_autospec` / `spec=`.
- **Testing private methods**: test through the public API instead. If you _really_ want to test a helper, it probably wants to be its own public function or class.
- **Dict/set ordering in assertions**: compare as sets or sorted lists if order isn't part of the contract.
- **Time-dependent tests**: inject the clock.
- **`pytest.raises` block too wide**: put only the line that should raise inside the `with`.

---

## 12. Katas to practice (do 2–3 before the interview)

Time-box each to 30–45 min, with strict red-green-refactor. Narrate out loud, even alone. Ideally record yourself once.

| Kata                                                   | Why it's good                                                              |
| ------------------------------------------------------ | -------------------------------------------------------------------------- |
| **FizzBuzz**                                           | Warm-up, parametrize, fake → triangulate                                   |
| **String Calculator** (Roy Osherove)                   | Incremental requirements, delimiters, exceptions for negatives             |
| **Roman Numerals**                                     | Triangulation, data-driven refactor to a lookup table                      |
| **Supermarket Checkout** (section 5)                   | State, offers, design decisions                                            |
| **Bowling Game** (Uncle Bob)                           | The classic. Spares/strikes force real design                              |
| **Gilded Rose**                                        | Refactoring legacy code: write characterization tests first, then refactor |
| **Bank Account / Kata** (deposit, withdraw, statement) | Injecting a clock, printing output, `capsys`                               |
| **Mars Rover**                                         | Commands, state, value objects, error handling                             |
| **Game of Life**                                       | Neighbor counting, boundaries, parametrize                                 |
| **Word Wrap**                                          | Good TPP exercise: shows when a step is too big                            |

Gilded Rose deserves a special mention: many "pair programming" interviews hand you existing ugly code. The move there is **characterization tests** (pin down current behavior, even if it's weird, with tests) and _then_ refactor under green. Approval/snapshot tests are fine for this.

String Calculator spec, so you can do it offline:

1. `add("")` returns 0; `add("1")` returns 1; `add("1,2")` returns 3.
2. Any amount of numbers.
3. Newlines are also delimiters: `"1\n2,3"` → 6.
4. Custom delimiter: `"//;\n1;2"` → 3.
5. Negatives raise with message `"negatives not allowed: -1, -3"` (list all of them).
6. Numbers > 1000 are ignored.
7. Delimiters of any length: `"//[***]\n1***2***3"` → 6.

Bowling spec: 10 frames. A frame is 2 rolls. Spare (10 in two rolls) → bonus is the next roll. Strike (10 on first roll) → bonus is next two rolls. 10th frame can have 1–2 bonus rolls. Perfect game = 300. Classic test order: gutter game (all 0) → all ones (20) → one spare → one strike → perfect game.

---

## 13. Cheat sheet (keep open during the call)

```text
LOOP     red (one small failing test, predict failure) → green (simplest pass) → refactor (on green only)
NEXT     zero → one → many → boundaries → errors     (ZOMBIES)
STUCK    smaller test. fake it. triangulate.
SAY      "I expect this to fail because..."  "Faking it, next test forces real logic."
         "This should pass already, adding it as a spec."  "Refactoring now, tests green."
```

```python
import pytest

@pytest.fixture
def thing(): ...

@pytest.mark.parametrize("given, expected", [(1, 2), (2, 4)])
def test_x(given, expected): assert f(given) == expected

with pytest.raises(ValueError, match="msg"): f(-1)
assert x == pytest.approx(0.3)

from unittest.mock import Mock, create_autospec, patch
m = create_autospec(Real, instance=True)
m.method.return_value = 42
m.method.side_effect = TimeoutError
m.method.assert_called_once_with("a")
@patch("module_under_test.name")   # where it's looked up
```

```bash
pytest -q -x            # fast loop
pytest -k name -vv      # one test, full diff
pytest --lf             # last failed
```

---

## Further reading

- Kent Beck, _Test-Driven Development: By Example_ — the original. Part I (the money example) is the best 2 hours you can spend.
- Freeman & Pryce, _Growing Object-Oriented Software, Guided by Tests_ — London school, outside-in.
- Harry Percival, _Test-Driven Development with Python_ (free online at obeythetestinggoat.com) — Python-specific, Django-heavy.
- Martin Fowler, [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) — classicist vs. mockist.
- [pytest docs: how-to guides](https://docs.pytest.org/en/stable/how-to/index.html)
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html), especially "where to patch".
- [kata-log.rocks](https://kata-log.rocks/) — catalog of katas with specs.
- [GeeksforGeeks: Test Driven Development](https://www.geeksforgeeks.org/software-engineering/test-driven-development-tdd) — the recruiter's link.
