# utils.py

"""Shared utility functions for the csvsee library.
"""

import csv
import re
from datetime import datetime, timedelta

from csvsee import dates

class NoMatch (Exception):
    """Exception raised when no column name matches a given expression."""
    pass


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


def column_names(csv_file):
    """Return a list of column names in the given ``.csv`` file.
    """
    reader = csv.DictReader(open(csv_file, 'r'))
    return reader.fieldnames


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


def grep_files(filenames, matches, dateformat='guess', resolution=60):
    """Search all the given files for matching text, and return a list of
    ``(timestamp, counts)`` for each match, where ``timestamp`` is a
    ``datetime``, and ``counts`` is a dictionary of ``{match: count}``,
    counting the number of times each match was found during intervals of
    ``resolution`` seconds.
    """
    # Counts of each match, used as a template for each row
    row_temp = [(match, 0) for match in matches]
    rows = {}
    # Read each line of each file
    for filename in filenames:
        # Guess date format?
        if not dateformat or dateformat == 'guess':
            dateformat = dates.guess_file_date_format(filename)

        # HACK: Fake timestamp in case no real timestamps are ever found
        timestamp = datetime(1970, 1, 1)
        for line in open(filename, 'r'):
            # If line is empty, skip it
            if line.strip() == '':
                continue

            # See if this line has a timestamp
            try:
                line_timestamp = dates.date_chop(line, dateformat, resolution)
            # No timestamp found, stick with the current one
            except dates.CannotParseDate:
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


def matching_fields(expr, fields):
    """Return all ``fields`` that match a regular expression ``expr``,
    or raise a `NoMatch` exception if no matches are found.

    Examples::

        >>> matching_fields('a.*', ['apple', 'banana', 'avocado'])
        ['apple', 'avocado']

        >>> matching_fields('a.*', ['peach', 'grape', 'kiwi'])
        Traceback (most recent call last):
        NoMatch: No matching column found for 'a.*'

    """
    # Do backslash-escape of expressions
    expr = expr.encode('unicode_escape')
    # Find matching fields
    matches = [field for field in fields if re.match(expr, field)]
    # Return matches or raise a NoMatch exception
    if matches:
        return matches
    else:
        raise NoMatch("No matching column found for '%s'" % expr)


def matching_xy_fields(x_expr, y_exprs, fieldnames, verbose=False):
    """Match ``x_expr`` and ``y_exprs`` to all available column names in
    ``fieldnames``, and return the matched ``x_column`` and ``y_columns``.

    Example::

        >>> matching_xy_fields('x.*', ['y[12]', 'y[ab]'],
        ...     ['xxx', 'y1', 'y2', 'y3', 'ya', 'yb', 'yc'])
        ('xxx', ['y1', 'y2', 'ya', 'yb'])

    If ``x_expr`` is empty, the first column name is used::

        >>> matching_xy_fields('', ['y[12]', 'y[ab]'],
        ...     ['xxx', 'y1', 'y2', 'y3', 'ya', 'yb', 'yc'])
        ('xxx', ['y1', 'y2', 'ya', 'yb'])

    If no match is found for any expression in ``y_exprs``, a `NoMatch`
    exception is raised::

        >>> matching_xy_fields('', ['y[12]', 'y[jk]'],
        ...     ['xxx', 'y1', 'y2', 'y3', 'ya', 'yb', 'yc'])
        Traceback (most recent call last):
        NoMatch: No matching column found for 'y[jk]'

    """
    # Make a copy of fieldnames
    fieldnames = [field for field in fieldnames]

    # If x_expr is provided, match on that.
    if x_expr:
        x_column = matching_fields(x_expr, fieldnames)[0]
    # Otherwise, just take the first field.
    else:
        x_column = fieldnames[0]

    #print("X-expression: '%s' matched column '%s'" % (x_expr, x_column))

    # In any case, remove the x column from fieldnames so it
    # won't be matched by any y-expression.
    fieldnames.remove(x_column)

    # Get all matching Y columns
    y_columns = []
    for y_expr in y_exprs:
        matches = matching_fields(y_expr, fieldnames)
        y_columns.extend(matches)
        #print("Y-expression: '%s' matched these columns:" % y_expr)
        #print('\n'.join(matches))

    return (x_column, y_columns)


def read_xy_values(reader, x_column, y_columns,
                   date_format='', gmt_offset=0, zero_time=False):
    """Read values from a `csv.DictReader`, and return ``(x_values,
    y_values)``. where ``x_values`` is a list of values found in ``x_column``,
    and ``y_values`` is a dictionary of ``{y_column: [values]}`` for each
    column in ``y_columns``.

    Arguments:

        x_column
            Name of the column you want to use as the X axis.

        y_columns
            Names of columns you want to plot on the Y axis.

        date_format
            If given, treat values in ``x_column`` as timestamps
            with the given format string.

        gmt_offset
            Add this many hours to every timestamp.
            Only useful with ``date_format``.

        zero_time
            If ``True``, adjust timestamps so the earliest one starts at
            ``00:00`` (midnight). Only useful with ``date_format``.

    """
    x_values = []
    y_values = {}

    for row in reader:
        x_value = row[x_column]

        # If X is supposed to be a date, try to convert it
        try:
            # FIXME: This could do weird things if the x-values
            # are sometimes parseable as dates, and sometimes not
            x_value = datetime.strptime(x_value, date_format) + \
                timedelta(hours=gmt_offset)
        # Otherwise, assume it's a floating-point numeric value
        except ValueError:
            x_value = float_or_0(x_value)

        x_values.append(x_value)

        # Append Y values from each column
        for y_col in y_columns:
            if y_col not in y_values:
                y_values[y_col] = []
            y_values[y_col].append(float_or_0(row[y_col]))

    # Adjust datestamps to start at 0:00?
    if date_format and zero_time:
        z = min(x_values)
        hms = timedelta(hours=z.hour, minutes=z.minute, seconds=z.second)
        x_values = [x - hms for x in x_values]

    return (x_values, y_values)


