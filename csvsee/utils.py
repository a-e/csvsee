# utils.py

"""Shared utility functions for the csvsee library.
"""

import sys
import csv
from datetime import datetime


def float_or_0(value):
    """Try to convert ``value`` to a floating-point number. If
    conversion fails, return ``0``.

    Examples::

        >>> float_or_0(5)
        5.0

        >>> float_or_0('5')
        5.0

        >>> float_or_0('five')
        0

    """
    try:
        return float(value)
    except ValueError:
        return 0


def guess_date_format(date_string):
    """Try to guess what format a given date/time string is in. If format can
    be inferred, return the format string. Otherwise, return an empty string.

    Examples::

        >>> guess_date_format('2010/01/28 13:25:49')
        '%Y/%m/%d %H:%M:%S'

        >>> guess_date_format('01/28/10 1:25:49 PM')
        '%m/%d/%y %I:%M:%S %p'

        >>> guess_date_format('01/28/2010 13:25:49.123')
        '%m/%d/%Y %H:%M:%S.%f'

    Some date strings are ambiguous; for example, '01/12/10' could mean "2010
    January 12", "2001 December 10", or even "2010 December 1". In these cases,
    the format guessed might be wrong.
    """
    # Date formats to try
    _formats = (
        '%Y/%m/%d %H:%M',
        '%Y/%m/%d %H:%M:%S',
        '%m/%d/%y %I:%M:%S %p',
        '%m/%d/%Y %H:%M:%S.%f',
    )
    # Try each format and return the first one that works
    for format in _formats:
        try:
            _result = datetime.strptime(date_string, format)
        except ValueError:
            pass
        else:
            return format
    return ''


def strip_prefix(strings):
    """Strip a common prefix from a sequence of strings.
    Return ``(prefix, [stripped])`` where ``prefix`` is the string that
    is common, and ``[stripped]`` is all strings with the prefix removed.

    Examples::

        >>> strip_prefix(['first', 'fourth', 'fifth'])
        ('f', ['irst', 'ourth', 'ifth'])

        >>> strip_prefix(['spam and eggs', 'spam and potatoes', 'spam and spam'])
        ('spam and ', ['eggs', 'potatoes', 'spam'])

    """
    prefix = ''
    # Group all first letters, then all second letters, etc.
    # letters list will be the same length as the shortest string
    for letters in zip(*strings):
        # If all letters are the same, append to common prefix
        if len(set(letters)) == 1:
            prefix += letters[0]
        else:
            break
    # Keep everything after the index where the strings diverge
    index = len(prefix)
    stripped = [s[index:] for s in strings]
    return (prefix, stripped)


def print_columns(csv_file):
    """Display column names in the given .csv file.
    """
    reader = csv.DictReader(open(csv_file, 'r'))
    columns = reader.fieldnames
    print("Column names found in '%s'" % csv_file)
    print('\n'.join(columns))


def date_chop(line, date_format='%m/%d/%y %I:%M:%S %p'):
    """Return the date/time portion of a given line, truncated to minutes.
    """
    # FIXME: Make this more generic, possibly using guess_date_format
    date_part = ' '.join(line.split()[0:3])
    timestamp = datetime.strptime(date_part, date_format)
    return timestamp.strftime('%Y/%m/%d %H:%M')


def grep_files(filenames, matches):
    """Search all the given files for matching text, and return
    a list of ``(match, count)`` for each match.
    """
    # Counts of each match, used as a template for each row
    row_temp = [(match, 0) for match in matches]
    rows = {}
    # Read each line of each file
    for filename in filenames:
        print("Reading '%s' ..." % filename)
        # HACK: Fake timestamp in case no real timestamps are ever found
        timestamp = "00:00"
        for line in open(filename, 'r'):
            # See if this line has a timestamp
            try:
                line_timestamp = date_chop(line)
            # No timestamp found, stick with the current one
            except ValueError:
                pass
            # New timestamp found, switch to it
            else:
                timestamp = line_timestamp

            # If this datestamp hasn't appeared before, add it
            if timestamp not in rows:
                rows[timestamp] = dict(row_temp)

            # Count the number of each match in this line
            for match in matches:
                if match in line:
                    rows[timestamp][match] += 1

    # Return a sorted list of (match, {counts}) tuples
    return sorted(rows.iteritems())

