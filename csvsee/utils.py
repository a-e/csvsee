# utils.py

"""Shared utility functions for the csvsee library.
"""

import csv
import re
import sys
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
    Return ``(prefix, [stripped])`` where ``prefix`` is the string that is
    common (with leading and trailing whitespace removed), and ``[stripped]``
    is all strings with the prefix removed.

    Examples::

        >>> strip_prefix(['first', 'fourth', 'fifth'])
        ('f', ['irst', 'ourth', 'ifth'])

        >>> strip_prefix(['spam and eggs', 'spam and potatoes', 'spam and spam'])
        ('spam and', ['eggs', 'potatoes', 'spam'])

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
    return (prefix.strip(), stripped)


def grep_files(filenames, matches, dateformat='guess', resolution=60,
               show_progress=True):
    """Search all the given files for matching text, and return a list of
    ``(timestamp, counts)`` for each match, where ``timestamp`` is a
    ``datetime``, and ``counts`` is a dictionary of ``{match: count}``,
    counting the number of times each match was found during intervals of
    ``resolution`` seconds.
    """
    # Counts of each match, used as a template for each row
    row_temp = [(match, 0) for match in matches]
    rows = {}

    # Compile regular expressions for matches
    # (Shaves off a little bit of execution time)
    compiled_matches = [re.compile(expr) for expr in matches]

    # Read each line of each file
    for filename in filenames:
        # Show progress bar?
        if show_progress:
            num_lines = line_count(filename)
            progress = ProgressBar(num_lines, prefix=filename, units='lines')
        # No progress bar, just print the filename being read
        else:
            print("Reading %s" % filename)

        # Guess date format?
        if not dateformat or dateformat == 'guess':
            dateformat = dates.guess_file_date_format(filename)

        # HACK: Fake timestamp in case no real timestamps are ever found
        timestamp = datetime(1970, 1, 1)
        # What line number are we on?
        line_num = 0
        for line in open(filename, 'r'):
            line_num += 1
            # Update progress bar every 1000 lines
            if show_progress:
                if line_num % 1000 == 0 or line_num == num_lines:
                    progress.update(line_num)
                    sys.stdout.write('\r' + str(progress))
                    sys.stdout.flush()

            # Remove leading/trailing whitespace and newlines
            line = line.strip()

            # If line is empty, skip it
            if not line:
                continue

            # See if this line has a timestamp
            try:
                line_timestamp = dates.date_chop(line, dateformat, resolution)
            # No timestamp found, stick with the current one
            except dates.CannotParse:
                pass
            # New timestamp found, switch to it
            else:
                timestamp = line_timestamp

            # If this datestamp hasn't appeared before, add it
            if timestamp not in rows:
                rows[timestamp] = dict(row_temp)

            # Count the number of each match in this line
            for expr in compiled_matches:
                if expr.search(line):
                    rows[timestamp][expr.pattern] += 1

        # If using progress bar, print a newline
        if show_progress:
            sys.stdout.write('\n')

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
    return sorted_columns[drop:drop + count]


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


def line_count(filename):
    """Return the total number of lines in the given file.
    """
    # Not terribly efficient but easy and good enough for now
    return sum(1 for line in open(filename))


class ProgressBar:
    """An ASCII command-line progress bar with percentage.

    Adapted from Corey Goldberg's version:
    http://code.google.com/p/corey-projects/source/browse/trunk/python2/progress_bar.py
    """
    def __init__(self, end, prefix='', fill='=', units='secs', width=40):
        """Create a progress bar with the given attributes.
        """
        self.end = end
        self.prog_bar = '[]'
        self.prefix = prefix
        self.fill = fill
        self.units = units
        self.width = width
        self._update_amount(0)

    def _update_amount(self, new_amount):
        """Update the progress bar with the percentage of completion.
        """
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[' + self.fill * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) / 2) - len(str(percent_done))
        pct_string = '%i%%' % percent_done
        self.prog_bar = self.prog_bar[0:pct_place] + \
            (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def update(self, current):
        """Set the current progress.
        """
        self._update_amount((current / float(self.end)) * 100.0)
        self.prog_bar += '  %d/%d %s' % (current, self.end, self.units)

    def __str__(self):
        """Return the progress bar as a string.
        """
        return str(self.prefix + ' ' + self.prog_bar)


def filter_csv(csv_infile, csv_outfile, columns, match='regexp', action='include'):
    """Filter ``csv_infile`` and write output to ``csv_outfile``.

        columns
            A list of regular expressions or exact column names
        match
            ``regexp`` to treat each value in ``columns`` as a regular
            expression, ``exact`` to match exact literal column names
        action
            ``include`` to keep the specified ``columns``, or ``exclude``
            to keep all columns *except* the specified ``columns``

    """
    # TODO: Factor out a 'filter_columns' function
    reader = csv.DictReader(open(csv_infile))
    # Do regular-expression matching of column names?
    if match == 'regexp':
        matching_columns = []
        for expr in columns:
            # TODO: What if more than one expression matches a column?
            # Find a way to avoid duplicates.
            matching_columns += matching_fields(expr, reader.fieldnames)
    # Exact matching of column names
    else:
        matching_columns = columns

    # Include or exclude?
    if action == 'include':
        keep_columns = matching_columns
    else:
        keep_columns = [col for col in reader.fieldnames
                        if col not in matching_columns]

    # Create writer for the columns we're keeping; ignore any extra columns
    # passed to the writerow() method.
    writer = csv.DictWriter(open(csv_outfile, 'w'), keep_columns,
                            extrasaction='ignore')
    # Write the header (csv.DictWriter doesn't do this for us)
    writer.writerow(dict(zip(keep_columns, keep_columns)))
    for row in reader:
        writer.writerow(row)


def boring_columns(csvfile):
    """Return a list of column names in ``csvfile`` that are "boring"--that is,
    the data in them is always the same.
    """
    # TODO: Consider columns that never deviate much (less than 1%, say)
    # to be boring also
    reader = csv.DictReader(open(csvfile))
    # Assume all columns are boring until they prove to be interesting
    boring = list(reader.fieldnames)
    # Remember the first value from each column
    prev = reader.next()
    for row in reader:
        # Check boring columns to see if they have become interesting yet
        # (make a copy to prevent problems with popping while iterating)
        for col in list(boring):
            # If previous value was empty, set prev to current
            # (this handles the case where a column is empty for a while,
            # then gets a value later). This is not inherently interesting.
            if not prev[col].strip():
                prev[col] = row[col]
            # If the current value is non-empty, and different from the
            # previous, then it's interesting
            elif row[col].strip() and row[col] != prev[col]:
                boring.remove(col)

    # Return names of all columns that never became interesting
    return boring


