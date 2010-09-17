# dates.py

"""Date/time parsing and manipulation functions
"""

from datetime import datetime
import time

class CannotParseDate (Exception):
    """Failure to parse a string as a date.
    """
    pass


def parse_date(string, format):
    """Attempt to parse the given string as a date in the given format.
    This is similar to `datetime.strptime`, but this can handle date strings
    with trailing characters. If it still fails to parse, raise a
    `CannotParseDate` exception.

    Examples::

        >>> parse_date('2010/08/28', '%Y/%m/%d')
        datetime.datetime(2010, 8, 28, 0, 0)

        >>> parse_date('2010/08/28 extra stuff', '%Y/%m/%d')
        datetime.datetime(2010, 8, 28, 0, 0)

        >>> parse_date('2010/08/28', '%m/%d/%y')
        Traceback (most recent call last):
        CannotParseDate: time data '2010/08/28' does not match format '%m/%d/%y'
    """
    try:
        result = datetime.strptime(string, format)
    except ValueError, err:
        # A bit of hack here, since strptime doesn't distinguish between
        # total failure to parse a date, and success with trailing
        # characters. This attempts to catch the possibility where a date
        # format matches, but there's extra stuff at the end.
        message = str(err)
        data_remains = 'unconverted data remains: '
        if message.startswith(data_remains):
            # Try again with the unconverted data removed
            junk = message[len(data_remains):]
            clean = string[:-1*len(junk)]
            result = datetime.strptime(clean, format)
        else:
            raise CannotParseDate(message)

    # If we got here, we got a result
    return result


def guess_date_format(string):
    """Try to guess what date/time format a given ``string`` is in. If format
    can be inferred, return the format string. Otherwise, raise a
    `CannotParseDate` exception.

    Examples::

        >>> guess_date_format('2010/01/28 13:25:49')
        '%Y/%m/%d %H:%M:%S'

        >>> guess_date_format('01/28/10 1:25:49 PM')
        '%m/%d/%y %I:%M:%S %p'

        >>> guess_date_format('01/28/2010 13:25:49.123')
        '%m/%d/%Y %H:%M:%S.%f'

    Some date strings are ambiguous; for example, ``01/12/10`` could mean "2010
    January 12", "2001 December 10", or even "2010 December 1". In these cases,
    the format guessed might be wrong.
    """
    # Date formats to try
    # (More specific ones are tried first, more general ones later)
    # FIXME: This is quickly getting out of control, with different ways of
    # combining dates and times, and could get much worse if alternate
    # separators are allowed ('/' vs. '-'). Find a way to simplify and
    # generalize this, or leverage an existing module like python-dateutil.
    _formats = (
        '%Y/%m/%d %I:%M:%S %p',
        '%m/%d/%Y %I:%M:%S %p',
        '%m/%d/%y %I:%M:%S %p',

        '%Y/%m/%d %I:%M %p',
        '%m/%d/%Y %I:%M %p',
        '%m/%d/%y %I:%M %p',

        '%Y/%m/%d %H:%M:%S.%f',
        '%m/%d/%Y %H:%M:%S.%f',
        '%m/%d/%y %H:%M:%S.%f',

        '%Y/%m/%d %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%y %H:%M:%S',

        '%Y/%m/%d %H:%M',
        '%m/%d/%Y %H:%M',
        '%m/%d/%y %H:%M',
    )
    # Try each format and return the first one that works
    for format in _formats:
        try:
            temp = parse_date(string, format)
        except CannotParseDate:
            pass
        else:
            return format

    raise CannotParseDate("Could not guess date format in: '%s'" % string)


def guess_file_date_format(filename):
    """Open the given file and use `guess_date_format` to look for a date/time
    at the beginning of each line. Return the format string for the first
    one that's found, or ``None`` if none are found.
    """
    for line in open(filename):
        try:
            format = guess_date_format(line)
        except CannotParseDate:
            pass
        else:
            return format

    raise CannotParseDate("No date/time strings found in '%s'" % filename)


def date_chop(line, dateformat='%m/%d/%y %I:%M:%S %p', resolution=60):
    """Given a ``line`` of text, get a date/time formatted as ``dateformat``,
    and return a `datetime` object rounded to the nearest ``resolution``
    seconds. If ``line`` fails to match ``dateformat``, a `CannotParseDate`
    exception is raised.

    Examples::

        >>> date_chop('1976/05/19 12:05:17', '%Y/%m/%d %H:%M:%S', 60)
        datetime.datetime(1976, 5, 19, 12, 5)

        >>> date_chop('1976/05/19 12:05:17', '%Y/%m/%d %H:%M:%S', 3600)
        datetime.datetime(1976, 5, 19, 12, 0)

    """
    timestamp = parse_date(line, dateformat)
    # Round the timestamp to the given resolution
    # First convert to seconds-since-epoch
    epoch_seconds = int(time.mktime(timestamp.timetuple()))
    # Then do integer division to truncate
    rounded_seconds = (epoch_seconds / resolution) * resolution
    # Convert back to a datetime
    return datetime.fromtimestamp(rounded_seconds)



