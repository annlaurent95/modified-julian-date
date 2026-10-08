"""Convert Modified Julian Dates used in satellite tracking to Gregorian dates.

This module operates in UT, like most tracking-system timestamps. It does not
describe a timezone or handle leap seconds: an MJD is a continuous count of
days since 1858-11-17T00:00:00 UT, and we translate that count into a calendar
representation whose hour field is the fractional-day component scaled to 24.
"""

from datetime import datetime, timedelta
import math

# The MJD origin, 1858-11-17 00:00:00 UTC, matches the conventional Modified
# Julian Date used across astronomy and satellite tracking. Tracked here as
# the Gregorian datetime so we can add days directly and land on a calendar
# date. This is the reference MJD for the Gregorian calendar; all satellite
# tracking systems use this exact origin.
MJD_EPOCH = datetime(1858, 11, 17, 0, 0, 0)

# The epoch where MJD 0 aligns with the Gregorian calendar. Exposed so callers
# can reason about the origin in their own code or documentation.
GREGORIAN_EPOCH_MJD = 0.0


def mjd_to_gregorian(mjd: float) -> datetime:
    """Convert a Modified Julian Date to a Gregorian ``datetime``.

    The input is a real number of days elapsed since 1858-11-17T00:00:00.
    Fractional days are converted to time-of-day. Because we use
    ``datetime.timedelta``, the resolution is one microsecond and the
    remaining sub-microsecond portion of the input is discarded.

    Parameters
    ----------
    mjd:
        Modified Julian Date as a count of days since the MJD epoch.

    Returns
    -------
    datetime
        The corresponding Gregorian date and time. The returned ``datetime``
        is naive: it carries no tzinfo, because MJD itself describes only a
        continuous day count without a timezone label.

    Raises
    ------
    ValueError
        If ``mjd`` is not finite or the result lies outside the range
        ``datetime`` supports.
    """
    if not isinstance(mjd, (int, float)):
        raise TypeError("mjd must be a real number")
    if math.isnan(mjd) or math.isinf(mjd):
        raise ValueError("mjd must be finite")

    # We separate the integer and fractional parts before arithmetic so that
    # floating-point noise near whole-day boundaries does not produce results
    # like 23:59:59.999999 for an input that should be exactly midnight. The
    # fractional part is kept as the remainder after flooring the whole-day
    # count, which is stable for both positive and negative inputs.
    whole_days = math.floor(mjd)
    fraction = mjd - whole_days

    # datetime.timedelta accepts floats but multiplies them in a way that can
    # introduce representation error for values that are not exactly
    # representable in binary. We convert to microseconds explicitly so the
    # rounding behaviour is well-defined and deterministic.
    total_microseconds = int(round(fraction * 86_400_000_000))
    if total_microseconds >= 86_400_000_000:
        whole_days += 1
        total_microseconds -= 86_400_000_000

    try:
        return MJD_EPOCH + timedelta(days=whole_days, microseconds=total_microseconds)
    except OverflowError as exc:
        raise ValueError(
            "mjd value results in a date outside the supported range"
        ) from exc


def mjd_to_gregorian_truncated(mjd: float) -> datetime:
    """Convert a Modified Julian Date to a Gregorian date at midnight.

    Satellite element sets such as TLEs frequently specify an epoch only to
    the whole day (or with a fractional day that callers want to discard for
    grouping). This function drops the fractional day and returns the date at
    00:00:00.

    Parameters
    ----------
    mjd:
        Modified Julian Date as a count of days since the MJD epoch.

    Returns
    -------
    datetime
        The Gregorian date at midnight. Naive, like
        :func:`mjd_to_gregorian`.

    Raises
    ------
    ValueError
        If ``mjd`` is not finite.
    """
    if not isinstance(mjd, (int, float)):
        raise TypeError("mjd must be a real number")
    if math.isnan(mjd) or math.isinf(mjd):
        raise ValueError("mjd must be finite")

    # We round to the nearest whole day so that an input like 58800.999999,
    # which is the noisy representation of 58801.0 in some upstream sources,
    # maps to the day the author of that input intended. A strict floor would
    # put it on the previous day.
    whole_days = math.floor(mjd + 0.5)
    try:
        return MJD_EPOCH + timedelta(days=whole_days)
    except OverflowError as exc:
        raise ValueError(
            "mjd value results in a date outside the supported range"
        ) from exc
