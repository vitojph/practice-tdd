# Practice kata: split an amount over a year

This is a practice spec inferred from the scaffold. It is not the interview problem. The README says that problem is shared at the start of the interview. Do not implement this inside `rillet-coding-challenge`. Practice it in a scratch folder.

Related: [TDD for Python: pair programming refresher](../practice-tdd/tdd-python-refresher.md), section 5 (supermarket checkout). This kata uses the same rhythm on the types already in this repo.

Time box: 30–45 minutes. Narrate out loud.

---

## What the scaffold is telling you

The unfinished seam is `SplitAmountsUseCase.execute(amount)`. It takes one `Money` and returns `Any`. The only behavior hint is the test name `test_returns_amounts_calculated_over_a_year`, with `dollars("1200")`.

`ResponseDto.from_result` is a second seam. Leave it until the use case is green. That is the same move as the checkout kata: one class, then an interface decision.

Two traps in the starter:

- `assert result is None` is already green. `execute` is `pass`, so it returns `None`. That test does not describe a behavior. Replace it. Do not celebrate that green.
- `amount / 12` looks right and is wrong. `py-money` rounds half up. `dollars("100") / 12` is `USD 8.33`. Twelve of those sum to `USD 99.96`. Four cents vanish. The checkout analogue is the running total that cannot do offers.

`Money` already has the tools: `amount.sub_units` and `Money.from_sub_units(cents, amount.currency)`. USD has 100 sub-units. JPY has 1. Do not hard-code `* 100`.

Useful `Money` facts from `py-money==0.5.0`:

- Construct with a string: `Money("1200", Currency.USD)`. Too many decimal places raises `InvalidAmountError`.
- `amount.sub_units` is an `int`. `Money.from_sub_units(834, Currency.USD)` is `USD 8.34`.
- `money / 12` returns a `Money`, rounded half up. It does not preserve the sum.
- `sum(result)` fails. `Money.__radd__` does not accept `0`. Use `sum(result, dollars("0"))`.
- Adding two `Money` values in different currencies raises `CurrencyMismatchError`.
- The test helper `dollars(n)` in `tests/helpers.py` builds `Money(n, Currency.USD)`. Production code should not import it.

---

## Spec

Split one `Money` into 12 monthly amounts. A year has 12 months. The method takes only `amount`. Do not add a month count until a test needs it.

Rules for this practice spec:

- Return 12 `Money` values.
- Each value uses `amount.currency`.
- The 12 values sum back to `amount`. No lost sub-unit. No extra sub-unit.
- Neighbors differ by at most one sub-unit.
- Extra sub-units go to the earliest months.

That last rule is a choice. In the interview, ask. Some schedules put the leftover on the last month. Pick one answer, test it, and say you are open to the other.

Examples, if extras go first:

| Input | Result |
| --- | --- |
| USD 1200.00 | twelve USD 100.00 |
| USD 2400.00 | twelve USD 200.00 |
| USD 100.00 | four USD 8.34, then eight USD 8.33 |
| USD 1.00 | four USD 0.09, then eight USD 0.08 |
| USD 0.01 | one USD 0.01, then eleven USD 0.00 |
| USD 10.00 | four USD 0.84, then eight USD 0.83 |
| USD 99.99 | three USD 8.34, then nine USD 8.33 |
| JPY 10 | ten JPY 1, then two JPY 0 |

How the uneven rows are calculated:

- USD 100.00 is 10000 sub-units. `divmod(10000, 12)` is `(833, 4)`. First 4 months get 834. The rest get 833.
- USD 1.00 is 100 sub-units. `divmod(100, 12)` is `(8, 4)`.
- USD 0.01 is 1 sub-unit. `divmod(1, 12)` is `(0, 1)`.
- USD 10.00 is 1000 sub-units. `divmod(1000, 12)` is `(83, 4)`.
- USD 99.99 is 9999 sub-units. `divmod(9999, 12)` is `(833, 3)`.
- JPY 10 is 10 sub-units, because JPY has 1 sub-unit per unit. `divmod(10, 12)` is `(0, 10)`.

`AmountDto` already rejects `value <= 0` and a bad currency code. The use case never sees those if the request comes through `create_amounts`. Do not re-test the DTO inside the use case.

---

## Test list

Write this at the top of the test file. Un-skip one at a time.

```python
# - USD 1200 is twelve USD 100          (replace the None assertion)
# - USD 2400 is twelve USD 200          (kills a hard-coded 100)
# - the 12 amounts sum to the input
# - USD 100: first 4 months get the extra cent
# - USD 0.01: only month 1 is non-zero
# - currency is preserved
# - JPY 10: do not assume 100 sub-units
# - ResponseDto.from_result maps the 12 amounts   (only if time)
```

Keep the existing test class. The shared `use_case = SplitAmountsUseCase()` is fine while `execute` is pure. Say that. If you add mutable state, move it to a fixture.

---

## Step 1: the planted case

Red. Replace the `None` assertion.

```python
def test_returns_amounts_calculated_over_a_year(self):
    result = self.use_case.execute(dollars("1200"))

    assert result == [dollars("100")] * 12
```

Predict the failure: `None != [USD 100.00, ...]`. Run it. Confirm that failure. An `ImportError` is the wrong red.

Green. Fake it.

```python
def execute(self, amount: Money) -> list[Money]:
    return [Money("100", amount.currency)] * 12
```

Say: "Faking 100. The next amount will force real division." `Money` is immutable, so one object repeated 12 times is fine for now.

---

## Step 2: triangulate

Red.

```python
def test_even_split_uses_the_amount(self):
    result = self.use_case.execute(dollars("2400"))

    assert result == [dollars("200")] * 12
```

Fails with twelve `100`s. Green, the attractive wrong one:

```python
def execute(self, amount: Money) -> list[Money]:
    month = amount / 12
    return [month] * 12
```

Both even tests pass. Say: "This rounds. I know it drops cents. That is the next test."

---

## Step 3: the sum

Red. This is the offer-plus-remainder moment.

```python
def test_parts_sum_to_the_original_amount(self):
    amount = dollars("100")
    result = self.use_case.execute(amount)

    assert sum(result, dollars("0")) == amount
```

`sum` needs a `Money` start value. `Money.__radd__` does not accept `0`. Predict `USD 99.96 != USD 100.00`.

Do not fix this by adding four cents onto the last item after dividing. That hides the bug. Switch to sub-units.

```python
MONTHS_IN_A_YEAR = 12


class SplitAmountsUseCase:
    def execute(self, amount: Money) -> list[Money]:
        base, extra = divmod(amount.sub_units, MONTHS_IN_A_YEAR)
        return [
            Money.from_sub_units(base + (1 if i < extra else 0), amount.currency)
            for i in range(MONTHS_IN_A_YEAR)
        ]
```

`divmod(10000, 12)` is `(833, 4)`. The first 4 months get 834 sub-units (`USD 8.34`). The rest get 833 (`USD 8.33`). The sum is 10000 sub-units.

Refactor on green: the name `MONTHS_IN_A_YEAR` is enough. Do not add a `Schedule` type yet.

---

## Step 4: where the extra cent goes

The sum test does not care about order. This test does.

```python
def test_extra_cents_go_to_the_earliest_months(self):
    result = self.use_case.execute(dollars("100"))

    assert result[:4] == [dollars("8.34")] * 4
    assert result[4:] == [dollars("8.33")] * 8
```

If step 3 put the extra on the earliest months, this is already green. Say so. If you expected red and got green, break the order briefly and watch it fail. Then put it back.

`USD 0.01` should also already pass: `divmod(1, 12)` is `(0, 1)`. Add it as a spec, not as a new discovery.

```python
def test_one_cent_lands_on_the_first_month_only(self):
    result = self.use_case.execute(dollars("0.01"))

    assert result[0] == dollars("0.01")
    assert result[1:] == [dollars("0")] * 11
```

---

## Step 5: currency, then collapse the tests

```python
def test_preserves_currency(self):
    amount = Money("1200", Currency.EUR)
    result = self.use_case.execute(amount)

    assert result == [Money("100", Currency.EUR)] * 12
```

This passes if you used `amount.currency`. Say that.

Then parametrize. Keep only cases you have already decided.

```python
@pytest.mark.parametrize(
    "raw, first, rest, extra_months",
    [
        ("1200", "100.00", "100.00", 0),
        ("2400", "200.00", "200.00", 0),
        ("100", "8.34", "8.33", 4),
        ("1", "0.09", "0.08", 4),
        ("0.01", "0.01", "0.00", 1),
        ("10", "0.84", "0.83", 4),
        ("99.99", "8.34", "8.33", 3),
    ],
)
def test_year_split(self, raw, first, rest, extra_months):
    result = self.use_case.execute(dollars(raw))

    assert result[:extra_months] == [dollars(first)] * extra_months
    assert result[extra_months:] == [dollars(rest)] * (12 - extra_months)
    assert sum(result, dollars("0")) == dollars(raw)
```

---

## Step 6: kill the cents assumption

Red, if you still have `* 100` anywhere. JPY has 1 sub-unit, not 100.

```python
def test_uses_currency_sub_units_not_cents(self):
    result = self.use_case.execute(Money("10", Currency.JPY))

    assert result[:10] == [Money("1", Currency.JPY)] * 10
    assert result[10:] == [Money("0", Currency.JPY)] * 2
```

`int(amount.amount * 100)` turns JPY 10 into 1000 and fails this. `amount.sub_units` passes it. If it passes on the first run, say it is a spec.

---

## What to ask instead of guessing

- Do leftover sub-units go to the first months or the last month?
- Is 12 fixed, or will the next requirement be a month count or a date range?
- Should `execute` reject zero or a negative `Money`, or is that only `AmountDto`'s job? `AmountDto.value` is `gt=0` already.
- What should `ResponseDto` look like? Do not invent fields. The request shape is `{"amount": {"value": ..., "currency": ...}}`. Matching that with an `amounts` list is a reasonable proposal. Ask before coding it.

Skip negatives unless they ask. Python `divmod(-100, 12)` is `(-9, 8)`, not `(-8, -4)`. A negative split written like the positive one will look plausible and be wrong.

---

## If time remains: the DTO

One test, through `ResponseDto.from_result`, not through HTTP. Same rhythm. Predict that `from_result` returns `None`.

Agree the JSON first. A symmetric shape is:

```json
{"amounts": [{"value": 100.0, "currency": "USD"}]}
```

`AmountDto.value` is a `float`. Say that floats are a bad money type. Match the request unless your pair wants both sides changed to a decimal string.

Do not start here. The use case is the checkout. The DTO is the prices-in-the-constructor decision.

The controller already does this:

```python
amount = Money(str(request.amount.value), Currency[request.amount.currency])
result = use_case.execute(amount)
return ResponseDto.from_result(result)
```

`str(request.amount.value)` stringifies a float. Say that out loud. Do not "fix" the controller during the use-case kata.

---

## Part 2: stretch rounds

The README asks for "more than just a minimal, bare-bones solution". These rounds are the likely follow-ups from your pair. Do them in order. Each round is a new test list. Time box: 15–20 minutes per round.

Do not start a round before the previous one is green and refactored. Stop at green when time runs out.

### Round A: dated months

New requirement: the schedule says which month each amount belongs to. The contract has a start date.

This is an interface decision. Ask before typing. One proposal:

```python
@dataclass(frozen=True)
class MonthlyAmount:
    month: date      # first day of the month
    amount: Money
```

`execute(amount, start)` returns `list[MonthlyAmount]`. That breaks every Part 1 test. Do a refactor first, on green:

1. Extract the split into `domain/`, for example `split_evenly(amount, parts) -> list[Money]`.
2. Move the Part 1 tests to `tests/accounting/domain/` and point them at `split_evenly`. They stay green.
3. The use case now calls `split_evenly(amount, 12)`. Still green.

Now red:

```python
def test_schedule_starts_in_the_start_month(self):
    result = self.use_case.execute(dollars("1200"), start=date(2026, 3, 1))

    assert result[0] == MonthlyAmount(month=date(2026, 3, 1), amount=dollars("100"))
```

Then the boundary. A March start ends in February of the next year:

```python
def test_schedule_crosses_the_year_boundary(self):
    result = self.use_case.execute(dollars("1200"), start=date(2026, 3, 1))

    assert [m.month for m in result][9:] == [date(2027, 1, 1), date(2027, 2, 1)]
    assert result[-1].month == date(2027, 2, 1)
```

You need month arithmetic. `dateutil` is not in `requirements.txt`. Do not add a dependency for one line:

```python
def add_months(start: date, n: int) -> date:
    index = start.month - 1 + n
    return date(start.year + index // 12, index % 12 + 1, 1)
```

Test `add_months` directly with parametrize: `(2026-03-01, 0)`, `(2026-12-01, 1)`, `(2026-03-01, 11)`.

Question for your pair: what does `start=date(2026, 3, 15)` mean? Round C answers it. In Round A, normalize to the first of the month and say so.

### Round B: variable term

New requirement: contracts can be 1, 6, 12 or 36 months.

`split_evenly(amount, parts)` already takes `parts`. Most of these pass on the first run. Say so.

| Input | Parts | Result |
| --- | --- | --- |
| USD 100.00 | 3 | one USD 33.34, then two USD 33.33 |
| USD 100.00 | 1 | one USD 100.00 |
| USD 1000.00 | 36 | 28 × USD 27.78, then 8 × USD 27.77 |

How the 36-month row is calculated: `divmod(100000, 36)` is `(2777, 28)`.

The red test is `parts=0`. Today it raises `ZeroDivisionError` from `divmod`. That is an accident, not a decision. Make it explicit:

```python
def test_rejects_zero_parts(self):
    with pytest.raises(ValueError, match="parts must be positive"):
        split_evenly(dollars("100"), 0)
```

The use case gets `months` as a parameter. Keep `12` as the default only if your pair agrees.

### Round C: daily proration

This is real revenue recognition. A contract runs from 15 January 2026 to 14 January 2027, both days included. Revenue is earned per day, not per month.

Rules:

- Each calendar month gets `amount × days_in_that_month / total_days`.
- The parts sum back to `amount` exactly.
- Leftover sub-units go to the months with the largest remainder. Ties go to the earliest month.

Trap: a 12-month contract that starts mid-month touches **13** calendar months. 17 days in January 2026, 14 days in January 2027.

Start with an amount that divides cleanly. 365 days, USD 365.00, so USD 1.00 per day:

| Month | Days | Amount |
| --- | --- | --- |
| 2026-01 | 17 | USD 17.00 |
| 2026-02 | 28 | USD 28.00 |
| 2026-03 | 31 | USD 31.00 |
| … | … | … |
| 2026-12 | 31 | USD 31.00 |
| 2027-01 | 14 | USD 14.00 |

Then the remainder case. USD 1000.00 over the same period:

| Month | Days | Exact sub-units | Floor | Final |
| --- | --- | --- | --- | --- |
| 2026-01 | 17 | 4657.53 | 4657 | **4658** |
| 2026-02 | 28 | 7671.23 | 7671 | **7672** |
| 31-day months (×6) | 31 | 8493.15 | 8493 | 8493 |
| 30-day months (×4) | 30 | 8219.17 | 8219 | 8219 |
| 2027-01 | 14 | 3835.62 | 3835 | **3836** |

The floors sum to 99997. Three sub-units are left. They go to the three largest remainders: 2027-01 (.62), 2026-01 (.53), 2026-02 (.23). The final sum is 100000.

Sketch, in integer sub-units only:

```python
def allocate(amount: Money, weights: list[int]) -> list[Money]:
    total = sum(weights)
    shares = [divmod(amount.sub_units * w, total) for w in weights]
    leftover = amount.sub_units - sum(base for base, _ in shares)
    by_remainder = sorted(range(len(weights)), key=lambda i: -shares[i][1])
    winners = set(by_remainder[:leftover])
    return [
        Money.from_sub_units(base + (1 if i in winners else 0), amount.currency)
        for i, (base, _) in enumerate(shares)
    ]
```

`sorted` is stable, so ties keep the earliest month first.

Refactor payoff: `split_evenly(amount, parts)` is `allocate(amount, [1] * parts)`. Equal weights give equal remainders. Ties go to the earliest months. That is exactly the Part 1 rule. Replace the body and keep all Part 1 tests green.

More tests for this round:

- A leap year. 1 March 2027 to 29 February 2028 is 366 days.
- A contract inside one month. 1–10 March is one part with the whole amount.
- `end` before `start` raises.

Question for your pair: does the product want even monthly amounts (Round A) or daily proration (Round C)? Both are valid accounting policies. Do not build a strategy pattern until a test needs both.

### Round D: the HTTP layer

Test `POST /amounts` end to end.

Trap: FastAPI's `TestClient` needs `httpx`. **`httpx` is not in `requirements.txt` and not in `.venv`.** Install it before the interview, or say it out loud when you get here. Ask before you change `requirements.txt`.

```python
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_post_amounts_returns_twelve_amounts():
    response = client.post("/amounts", json={"amount": {"value": 1200, "currency": "USD"}})

    assert response.status_code == 200
    assert len(response.json()["amounts"]) == 12
```

`tests/__init__.py` puts `src/` on the path, so `from main import app` works.

These pass on the first run, because `AmountDto` already does the work. Add them as characterization tests and say so:

- `value: 0` returns 422 (`gt=0`).
- `currency: "usd"` returns 422. The check is case sensitive. `"USD" in Currency` is `True`. `"usd" in Currency` is `False`.

### Round E: float input

`AmountDto.value` is a `float`. The controller does `Money(str(request.amount.value), ...)`. These floats are valid for the DTO and break `Money`:

| JSON value | `str(value)` | `Money(...)` |
| --- | --- | --- |
| `0.1 + 0.2` | `0.30000000000000004` | `InvalidAmountError` |
| `1e-7` | `1e-07` | `InvalidAmountError` |
| `10.005` | `10.005` | `InvalidAmountError` |

Nothing catches `InvalidAmountError`. A real server returns 500. `TestClient` re-raises the exception in the test by default.

Red: post `10.005` USD and expect 422. Then discuss the fix with your pair:

- Change `value` to `Decimal` or a decimal string. This is the right money type. It changes the API contract.
- Validate decimal places in the DTO. The limit depends on the currency: USD has 2, JPY has 0. That needs a `model_validator`, not a `Field` constraint.
- Catch `InvalidAmountError` in the controller and return 422. This is the smallest change, but the validation then lives in two places.

---

## What to take from this

- The scaffold's green `None` test is not a behavior. Replace it first.
- Fake twelve `100`s. The second amount removes the fake.
- `amount / 12` is the wrong model, same as a running total that cannot do offers. The next test should expose it. Do not fix it early.
- The invariant is the sum, in sub-units. Order of leftover cents is a separate test and a question for your pair.
- Use `sub_units` and `from_sub_units`. A JPY case stops you from baking in cents.
- Before you change a return type, extract the logic to `domain/` and move its tests. Then change the use case.
- An even split is a weighted allocation with equal weights. The Round C refactor keeps every Part 1 test green.
- A mid-month start touches 13 calendar months. Days, not months, are the unit for proration.
- Check the tooling early. `TestClient` needs `httpx`, and the repo does not have it.
- A `float` money field is a bug waiting for a test. Name it, and let your pair choose the fix.
