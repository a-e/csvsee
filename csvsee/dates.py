# dates.py

"""Date/time parsing and manipulation functions
"""

# Some people, when confronted with a problem, think
#   "I know, I'll use regular expressions."
# Now they have two problems.
#                               -- Jamie Zawinski

import datetime as dt
import time
import re

_months = [
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'september',
    'october',
    'november',
    'december',
]

# Formatting directives and corresponding regular expression
_regexps = {
    'B': r'(?P<b>' + '|'.join(_months) + ')',
    'b': r'(?P<b>' + '|'.join(m[0:3] for m in _months) + ')',
    'm': r'(?P<m>\d\d?)',
    'd': r'(?P<d>\d\d?)',
    'Y': r'(?P<Y>\d\d\d\d)',
    'y': r'(?P<y>\d\d)',
    'I': r'(?P<H>0?[1-9]|1[012])',
    'H': r'(?P<H>[01]?[0-9]|2[0-3])',
    'M': r'(?P<M>[0-5]\d)',
    'S': r'(?P<S>[0-5]\d)',
    'f': r'(?P<f>\d+)',
    'p': r'(?P<p>am|pm)',
}

# Support date formats and examples
_date_formats = [
    'B d, Y',       # October 15, 2006
    'b d, Y',       # Oct 15, 2006
    'B d Y',        # October 15 2006
    'b d Y',        # Oct 15 2006
    'B d',          # October 15
    'b d',          # Oct 15
    'Y/m/d',        # 2006/10/15
    'Y-m-d',        # 2006-10-15
    'm/d/Y',        # 10/15/2006
    'm-d-Y',        # 10-15-2006
    'm/d/y',        # 10/15/06
    'm-d-y',        # 10-15-06
    'y/m/d',        # 06/10/15
    'y-m-d',        # 06-10-15
]

# Supported time formats and examples
_time_formats = [
    'I:M:S.f p',    # 3:05:29.108 PM
    'H:M:S.f',      # 15:05:29.108
    'I:M:S p',      # 3:05:29 PM
    'H:M:S',        # 15:05:29
    'I:M p',        # 3:05 PM
    'H:M',          # 15:05
]


class CannotParse (Exception):
    """Failure to parse a date or time.
    """
    pass


def parse(string, format):
    """Attempt to parse the given string as a date in the given format.
    This is similar to `datetime.strptime`, but this can handle date strings
    with trailing characters. If it still fails to parse, raise a
    `CannotParse` exception.

    Examples::

        >>> parse('2010/08/28', '%Y/%m/%d')
        datetime.datetime(2010, 8, 28, 0, 0)

        >>> parse('2010/08/28 extra stuff', '%Y/%m/%d')
        datetime.datetime(2010, 8, 28, 0, 0)

        >>> parse('2010/08/28', '%m/%d/%y')
        Traceback (most recent call last):
        CannotParse: time data '2010/08/28' does not match format '%m/%d/%y'

    """
    # Count the number of spaces in the format string (N), and
    # truncate everything after the (N+1)th space
    spaces = format.count(' ') + 1
    string = ' '.join(string.split()[:spaces])

    try:
        result = dt.datetime.strptime(string, format)
    except ValueError, err:
        raise CannotParse(str(err))
    else:
        return result


def format_regexp(simple_format):
    r"""Given a simplified date or time format string, return ``(format,
    regexp)``, where ``format`` is a `strptime`-compatible format string, and
    ``regexp`` is a regular expression that matches dates or times in that
    format.

    The ``simple_format`` string supports a subset of `strptime` formatting
    directives, with the leading ``%`` characters removed.

    Examples::

        >>> format_regexp('Y/m/d')
        ('%Y/%m/%d', '(?P<Y>\\d\\d\\d\\d)/(?P<m>\\d\\d?)/(?P<d>\\d\\d?)')

        >>> format_regexp('H:M:S')
        ('%H:%M:%S', '(?P<H>[01]?[0-9]|2[0-3]):(?P<M>[0-5]\\d):(?P<S>[0-5]\\d)')

    """
    format, regexp = ('', '')
    for char in simple_format:
        if char in _regexps:
            format += '%' + char
            regexp += _regexps[char]
        else:
            format += char
            regexp += char
    return (format, regexp)


def compiled_format_regexps(date_formats, time_formats):
    """Return a list of ``(format, compiled_regexp)`` for all combinations
    of ``date_formats`` and ``time_formats``.
    """
    # List of all combinations of date_formats and time_formats
    date_time_formats = []
    for df in date_formats:
        for tf in time_formats:
            date_time_formats.append(df + ' ' + tf)

    # Add date-only formats
    for df in date_formats:
        date_time_formats.append(df)

    # Add time-only formats
    for tf in time_formats:
        date_time_formats.append(tf)

    # (format, compiled_regexp) for each supported format
    format_regexps = []
    for dt_format in date_time_formats:
        format, regexp = format_regexp(dt_format)
        # Compile the regexp
        format_regexps.append(
            (format, re.compile(regexp, re.IGNORECASE))
        )

    return format_regexps


def guess_format(string):
    """Try to guess the date/time format of ``string``, or raise a
    `CannotParse` exception.

    Examples::

        >>> guess_format('2010/01/28 13:25:49')
        '%Y/%m/%d %H:%M:%S'

        >>> guess_format('01/28/10 1:25:49 PM')
        '%m/%d/%y %I:%M:%S %p'

        >>> guess_format('01/28/2010 13:25:49.123')
        '%m/%d/%Y %H:%M:%S.%f'

        >>> guess_format('Aug 15 2009 15:24')
        '%b %d %Y %H:%M'

        >>> guess_format('3-14-15 9:26:53.589')
        '%m-%d-%y %H:%M:%S.%f'

    Leading and trailing text may be present::

        >>> guess_format('FOO April 1, 2007 3:45 PM BAR')
        '%B %d, %Y %I:%M %p'

        >>> guess_format('[[2010-09-25 14:19:24]]')
        '%Y-%m-%d %H:%M:%S'

    """
    format_regexps = compiled_format_regexps(_date_formats, _time_formats)
    for format, regexp in format_regexps:
        if regexp.search(string):
            return format
    # Nothing matched
    raise CannotParse("Could not guess date/time format in: %s" % string)


def guess_file_date_format(filename):
    """Open the given file and use `guess_format` to look for a
    date/time at the beginning of each line. Return the format string for
    the first one that's found. Raise `CannotParse` if none is found.
    """
    for line in open(filename):
        try:
            format = guess_format(line)
        except CannotParse:
            pass
        else:
            return format

    raise CannotParse("No date/time strings found in '%s'" % filename)


def date_chop(line, dateformat='%m/%d/%y %I:%M:%S %p', resolution=60):
    """Given a ``line`` of text, get a date/time formatted as ``dateformat``,
    and return a `datetime` object rounded to the nearest ``resolution``
    seconds. If ``line`` fails to match ``dateformat``, a `CannotParse`
    exception is raised.

    Examples::

        >>> date_chop('1976/05/19 12:05:17', '%Y/%m/%d %H:%M:%S', 60)
        datetime.datetime(1976, 5, 19, 12, 5)

        >>> date_chop('1976/05/19 12:05:17', '%Y/%m/%d %H:%M:%S', 3600)
        datetime.datetime(1976, 5, 19, 12, 0)

    """
    timestamp = parse(line, dateformat)
    # Round the timestamp to the given resolution
    # First convert to seconds-since-epoch
    epoch_seconds = int(time.mktime(timestamp.timetuple()))
    # Then do integer division to truncate
    rounded_seconds = (epoch_seconds / resolution) * resolution
    # Convert back to a datetime
    return dt.datetime.fromtimestamp(rounded_seconds)


