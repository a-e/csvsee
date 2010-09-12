# utils.py

"""Shared utility functions for the csvsee library.
"""

import sys
import csv
from datetime import datetime
import time


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

    Some date strings are ambiguous; for example, '01/12/10' could mean "2010
    January 12", "2001 December 10", or even "2010 December 1". In these cases,
    the format guessed might be wrong.
    """
    # Date formats to try
    # (More specific ones are tried first, more general ones later)
    # FIXME: This could quickly get out of control, with different ways of
    # combining dates and times, especially if alternate separators are
    # allowed ('/' vs. '-'). Find a way to simplify and generalize this.
    _formats = (
        '%Y/%m/%d %I:%M:%S %p',
        '%m/%d/%Y %I:%M:%S %p',
        '%m/%d/%y %I:%M:%S %p',

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
    """Open the given file and look for anything that looks like a date/time
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


def grep_files(filenames, matches,
               dateformat='guess',
               resolution=60):
    """Search all the given files for matching text, and return a list of
    ``(timestamp, counts)`` for each match, where ``timestamp`` is a
    ``datetime``, and ``counts`` is a dictionary of ``{match: count}``,
    counting the number of times each match was found during that interval.
    """
    # Counts of each match, used as a template for each row
    row_temp = [(match, 0) for match in matches]
    rows = {}
    # Read each line of each file
    for filename in filenames:
        print("Reading '%s' ..." % filename)
        # Guess date format?
        if not dateformat or dateformat == 'guess':
            dateformat = guess_file_date_format(filename)

        # HACK: Fake timestamp in case no real timestamps are ever found
        timestamp = datetime(1970, 1, 1)
        for line in open(filename, 'r'):
            # If line is empty, skip it
            if line.strip() == '':
                continue

            # See if this line has a timestamp
            try:
                line_timestamp = date_chop(line, dateformat, resolution)
            # No timestamp found, stick with the current one
            except CannotParseDate:
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


def top_by(func, count, y_columns, y_values, drop=0):
    """Apply ``func`` to each column, and return the top ``count`` column
    names. Arguments:

        func
            A function that takes a list of values and returns a single value.
            `max`, `min`, and average are good examples.
        count
            How many of the "top" values to keep
        y_columns
            A list of candidate column names. All of these must
            exist as keys in ``y_values``
        y_values
            Dictionary of ``{column: values}`` for each y-column. Must have
            data for each column in ``y_columns`` (any extra column data will
            be ignored).
        drop
            How many top values to skip before returning the next
            ``count`` top columns

    """
    # List of (func(ys), y_name)
    results = []
    for y_name in y_columns:
        f_ys = func(y_values[y_name])
        results.append((f_ys, y_name))
    # Keep the top ``count`` after dropping ``drop`` values
    sorted_columns = [y_name for (f_ys, y_name) in reversed(sorted(results))]
    return sorted_columns[drop:drop+count]


def top_by_average(count, y_columns, y_values, drop=0):
    """Determine the top ``count`` columns based on the average of values
    in ``y_values``, and return the filtered ``y_columns`` names.
    """
    def avg(values):
        return float(sum(values)) / len(values)
    return top_by(avg, count, y_columns, y_values, drop)


def top_by_peak(count, y_columns, y_values, drop=0):
    """Determine the top ``count`` columns based on the peak value
    in ``y_values``, and return the filtered ``y_columns`` names.
    """
    return top_by(max, count, y_columns, y_values, drop)


def match_columns(fieldnames, x_expr, y_exprs):
    """Match `x_expr` and `y_exprs` to all available column names in
    `fieldnames`. Return the matched `x_column` and `y_columns`. If no matches
    are found for any expression, raise a `NoMatch` exception.
    """
    # Make a copy of fieldnames
    fieldnames = [field for field in fieldnames]

    def _matches(expr, fields):
        """Return a list of matching column names for `expr`,
        or raise a `NoMatch` exception if there were none.
        """
        # Do backslash-escape of expressions
        expr = expr.encode('unicode_escape')
        columns = [column for column in fields
                   if re.match(expr, column)]
        if columns:
            print("Expression: '%s' matched these columns:" % expr)
            print('\n'.join(columns))
            return columns
        else:
            raise NoMatch("No matching column found for '%s'" % expr)

    # If x_expr is provided, match on that.
    if x_expr:
        x_column = _matches(x_expr, fieldnames)[0]
    # Otherwise, just take the first field.
    else:
        x_column = fieldnames[0]

    # In any case, remove the x column from fieldnames so it
    # won't be matched by any y-expression.
    fieldnames.remove(x_column)

    # Get all matching Y columns
    y_columns = sum([_matches(y_expr, fieldnames)
                     for y_expr in y_exprs],
                    [])

    return (x_column, y_columns)


