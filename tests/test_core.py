import math
import unittest
from datetime import datetime

from modified_julian_date import (
    mjd_to_gregorian,
    mjd_to_gregorian_truncated,
    GREGORIAN_EPOCH_MJD,
)


class TestMjdToGregorian(unittest.TestCase):
    def test_epoch(self):
        # MJD 0 is the conventional origin: 1858-11-17 00:00:00.
        self.assertEqual(mjd_to_gregorian(0.0), datetime(1858, 11, 17, 0, 0, 0))
        self.assertEqual(GREGORIAN_EPOCH_MJD, 0.0)

    def test_known_date(self):
        # MJD 51544 is 2000-01-01 00:00:00, the J2000 epoch.
        self.assertEqual(mjd_to_gregorian(51544.0), datetime(2000, 1, 1, 0, 0, 0))

    def test_fractional_day(self):
        # 0.5 day = 12:00:00. Verifies the fractional-to-time conversion.
        self.assertEqual(
            mjd_to_gregorian(51544.5), datetime(2000, 1, 1, 12, 0, 0)
        )

    def test_quarter_day(self):
        self.assertEqual(
            mjd_to_gregorian(51544.25), datetime(2000, 1, 1, 6, 0, 0)
        )

    def test_three_quarter_day(self):
        self.assertEqual(
            mjd_to_gregorian(51544.75), datetime(2000, 1, 1, 18, 0, 0)
        )

    def test_microsecond_precision(self):
        # 0.000001 day is 1 day / 1_000_000, which is 0.0864 seconds, or
        # 86400 microseconds. We pick a value that lands exactly on a
        # microsecond boundary to avoid float comparison noise.
        one_microsecond_in_days = 1 / 86_400_000_000
        dt = mjd_to_gregorian(51544.0 + one_microsecond_in_days)
        self.assertEqual(dt, datetime(2000, 1, 1, 0, 0, 0, 1))

    def test_near_whole_day_does_not_roll_back(self):
        # A value one ulp above a whole day should not be reported as the
        # previous day at 23:59:59.999999. The implementation rounds the
        # fractional part, so this lands on the intended whole day.
        epsilon = 1e-9
        dt = mjd_to_gregorian(51544.0 + epsilon)
        self.assertEqual(dt.date(), datetime(2000, 1, 1).date())

    def test_negative_mjd_before_epoch(self):
        # MJD -1 is 1858-11-16 00:00:00.
        self.assertEqual(mjd_to_gregorian(-1.0), datetime(1858, 11, 16, 0, 0, 0))

    def test_integer_input(self):
        self.assertEqual(mjd_to_gregorian(51544), datetime(2000, 1, 1, 0, 0, 0))

    def test_rejects_nan(self):
        with self.assertRaises(ValueError):
            mjd_to_gregorian(float("nan"))

    def test_rejects_inf(self):
        with self.assertRaises(ValueError):
            mjd_to_gregorian(float("inf"))
        with self.assertRaises(ValueError):
            mjd_to_gregorian(float("-inf"))

    def test_rejects_non_numeric(self):
        with self.assertRaises(TypeError):
            mjd_to_gregorian("51544")  # type: ignore[arg-type]


class TestMjdToGregorianTruncated(unittest.TestCase):
    def test_epoch(self):
        self.assertEqual(
            mjd_to_gregorian_truncated(0.0), datetime(1858, 11, 17, 0, 0, 0)
        )

    def test_drops_fraction(self):
        # The fractional day is discarded and the date lands at midnight.
        # Values below .5 stay on the same day.
        self.assertEqual(
            mjd_to_gregorian_truncated(51544.25), datetime(2000, 1, 1, 0, 0, 0)
        )

    def test_rounds_to_nearest_day(self):
        # Values at or above .5 round to the next day, matching the
        # nearest-day behaviour documented for this function.
        self.assertEqual(
            mjd_to_gregorian_truncated(51543.5), datetime(2000, 1, 1, 0, 0, 0)
        )

    def test_rejects_nan(self):
        with self.assertRaises(ValueError):
            mjd_to_gregorian_truncated(float("nan"))


if __name__ == "__main__":
    unittest.main()
