# modified_julian_date

Converts Modified Julian Dates used in satellite tracking to Gregorian calendar dates, using only the Python standard library.

```python
from modified_julian_date import mjd_to_gregorian, mjd_to_gregorian_truncated

# MJD 51544.0 is 2000-01-01 00:00:00.
dt = mjd_to_gregorian(51544.5)
# -> datetime(2000, 1, 1, 12, 0, 0)

# Drop the fractional day, for grouping by whole days.
day = mjd_to_gregorian_truncated(51544.75)
# -> datetime(2000, 1, 1, 0, 0, 0)
```

## Why this exists

Satellite element sets and tracking feeds quote epochs as Modified Julian Dates: a continuous count of days since 1858-11-17T00:00:00 UT. Most downstream tooling wants a Gregorian date. The standard library can do the arithmetic once the epoch is pinned down, so the value here is not cleverness but a small, tested wrapper that fixes the epoch and the rounding behaviour in one place rather than re-deriving it each project.

The trade-off is that this library is UT-only and ignores leap seconds. MJD counts days; a leap second is not a day, so it has no representation in the input and is therefore absent from the output.

## Edge you will hit

Fractional days are not exactly representable in binary floating point. An input written as `51544.9999999` may be the noisy encoding of `51545.0`. `mjd_to_gregorian` rounds the fractional part to the nearest microsecond before composing the time of day, and `mjd_to_gregorian_truncated` rounds to the nearest whole day, so values just below a whole-day boundary land on the day the input's author most likely intended rather than on the previous day at 23:59:59.999999.

The returned `datetime` is naive. MJD describes a continuous day count, not a timezone, so attaching a tzinfo would be inventing information the input does not carry.

## Exports

- `mjd_to_gregorian(mjd: float) -> datetime` — full date and time to microsecond resolution.
- `mjd_to_gregorian_truncated(mjd: float) -> datetime` — date at midnight, fractional day discarded.
- `GREGORIAN_EPOCH_MJD` — the MJD value (0.0) whose Gregorian date is the MJD epoch.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

