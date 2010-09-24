# dates.py

"""Date/time parsing and manipulation functions
"""

# Grinder: 8/30/10 1:13:17 PM
# Maillong: Sep 21 18:10:38
# Perfmon: 12/01/2009 12:59:28.114
# csvs grep: 08/30/2010 19:10:00.000

import datetime as dt
import time
import re

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
    try:
        result = dt.datetime.strptime(string, format)
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
            result = dt.datetime.strptime(clean, format)
        else:
            raise CannotParse(message)

    # If we got here, we got a result
    return result


# Some people, when confronted with a problem, think
#   "I know, I'll use regular expressions."
# Now they have two problems.
#                               -- Jamie Zawinski

# Formatting directives and corresponding regular expression
_regexps = {
    'b': r'(?P<b>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
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

# Support date formats
_date_formats = [
    'b d Y',
    'b d',
    'Y/m/d',
    'Y-m-d',
    'm/d/Y',
    'm-d-Y',
    'm/d/y',
    'm-d-y',
    'y/m/d',
    'y-m-d',
]

# Supported time formats
_time_formats = [
    'I:M:S.f p',
    'H:M:S.f',
    'I:M:S p',
    'H:M:S',
    'I:M p',
    'H:M',
]

# All date/time formats combined
_date_time_formats = [
    df + ' ' + tf
    for df in _date_formats
        for tf in _time_formats
]

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


# (format, regexp) for each supported format
_format_regexps = []
for dt_format in _date_time_formats:
    format, regexp = format_regexp(dt_format)
    # Compile the regexp
    _format_regexps.append(
        (format, re.compile(regexp, re.IGNORECASE))
    )


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

    """
    for format, regexp in _format_regexps:
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



