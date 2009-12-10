#! /usr/bin/env python
# csvgraph.py

"""Generate graphs from .csv data files.
"""

usage = """Usage:

    csvgraph.py [-options] filename.csv "X column" "Y column 1" ["Y column 2"] ...

Where filename.csv contains comma-separated values, with column names in the
first row, and all subsequent arguments are regular expressions that may match
one or more column names.

Options:

    -title "TITLE"      Title label for the graph

At least one X-column and one Y-column must be provided; if any Y-column
expression matches multiple column names, and/or if multiple Y-column
expressions are provided, then all matching columns will be included in the
graph.

If the X-column is a date field, then the X axis will be displayed in HH:MM
format. Otherwise, all columns must be numeric (integer or floating-point).
"""

import csv
import sys
from datetime import datetime, timedelta
import pylab
from matplotlib import dates
import re

class NoMatch (Exception): pass

def usage_error(message):
    """Print a usage error, along with a custom message, then exit.
    """
    print(usage)
    print(message)
    sys.exit(1)


def to_datetime(dt_string, format='%m/%d/%Y %H:%M:%S.%f'):
    """Convert a given date/time string to a `datetime` object.
    """
    return datetime.strptime(dt_string, format)


def float_or_0(value):
    """Try to convert ``value`` to a floating-point number. If
    conversion fails, return 0.
    """
    try:
        return float(value)
    except ValueError:
        return 0


def match_columns(x_expr, y_exprs, fieldnames):
    """Match ``x_expr`` and ``y_exprs`` to all available column
    names in ``fieldnames``. Return the matched ``x_column`` and
    ``y_columns``. If no matches are found for any expression,
    raise a ``NoMatch`` exception.
    """
    def _matches(expr):
        """Return a list of matching column names for ``expr``,
        or raise a ``NoMatch`` exception if there were none.
        """
        # Do backslash-escape of expressions
        expr = expr.encode('unicode_escape')
        columns = [column for column in fieldnames if re.match(expr, column)]
        if columns:
            print("Expression: '%s' matched these columns:" % expr)
            print('\n'.join(columns))
            return columns
        else:
            raise NoMatch("No matching column found for '%s'" % expr)

    # Get the first matching X column, and all matching Y columns
    x_column = _matches(x_expr)[0]
    y_columns = sum([_matches(y_expr) for y_expr in y_exprs], [])

    return (x_column, y_columns)


def add_date_labels(axes, min_date, max_date):
    """Add date labels to the given Axes.
    """
    axes.set_xlim(min_date, max_date)
    date_range = max_date - min_date

    # If date range is more than 2 hours, label each hour
    if date_range > timedelta(hours=2):
        axes.xaxis.set_major_locator(dates.HourLocator())

    # If date range is more than 30 minutes, label 10-minute increments
    elif date_range > timedelta(minutes=30):
        axes.xaxis.set_major_locator(dates.MinuteLocator(interval=10))

    # If date range is more than 10 minutes, label every 5 minutes
    elif date_range > timedelta(minutes=10):
        axes.xaxis.set_major_locator(dates.MinuteLocator(interval=5))

    # If date range is 10 minutes or less, label every minute
    else:
        axes.xaxis.set_major_locator(dates.MinuteLocator())

    # Use HH:MM format for all labels
    axes.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))


def read_csv_values(reader, x_column, y_columns):
    """Read values from a csv `DictReader`, and return all values in
    `x_column` and `y_columns`.
    """
    x_is_date = False
    x_values = []
    y_values = {}
    for row in reader:
        x_value = row[x_column]
        # Try converting X value to datetime
        try:
            x_value = to_datetime(x_value)
        # If not a date, treat as a float
        except ValueError:
            x_value = float_or_0(x_value)
        else:
            x_is_date = True

        x_values.append(x_value)

        # Append Y values from each column
        for y_col in y_columns:
            if y_col not in y_values:
                y_values[y_col] = []
            y_values[y_col].append(float_or_0(row[y_col]))

    return x_values, y_values, x_is_date


def do_graph(csvfile, x_expr, y_exprs, title=''):
    """Generate a graph from `csvfile`, with `x_expr` defining the x-axis,
    and `y_exprs` being columns to get y-values from.
    """
    print("Reading '%s'" % csvfile)
    reader = csv.DictReader(open(csvfile, 'r'))

    # Attempt to match column names
    try:
        x_column, y_columns = match_columns(x_expr, y_exprs, reader.fieldnames)
    except NoMatch, err:
        usage_error(err)

    # Confirm with the user
    answer = raw_input("Graph these %d columns? " % len(y_columns))
    if answer.lower() != 'y':
        print("Quitting.")
        sys.exit(0)

    # Read each row in the .csv file and populate x and y value lists
    x_values, y_values, x_is_date = read_csv_values(reader, x_column, y_columns)

    # Create the figure and plot
    figure = pylab.figure()
    axes = figure.add_subplot(111, xlabel=x_column)
    axes.grid(True)

    if title:
        figure.suptitle(title, fontsize=18)

    # Do date formatting if the X column was a date field
    if x_is_date:
        min_date, max_date = min(x_values), max(x_values)
        add_date_labels(axes, min_date, max_date)
        figure.autofmt_xdate()

    # Plot lines for all Y columns
    lines = []
    for y_col in y_columns:
        line = axes.plot(x_values, y_values[y_col])
        lines.append(line)

    # Draw a legend for the figure
    legend = figure.legend(lines, y_columns, 'lower center')
    #legend.get_frame().set_alpha(0.5)

    # Show the graph viewer
    pylab.show()


# Main program
if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage_error("Need a filename and at least two column names")
    else:
        args = sys.argv[1:]

    title = ''

    # Get -options
    while args[0].startswith('-'):
        arg = args.pop(0)
        if arg == '-title':
            title = args.pop(0)

    # Get positional arguments
    csvfile = args.pop(0)
    x_expr = args.pop(0)
    y_exprs = args

    # Generate the graph
    do_graph(csvfile, x_expr, y_exprs, title)


