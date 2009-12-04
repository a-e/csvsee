#! /usr/bin/env python
# csvgraph.py

"""Generate graphs from .csv data files.
"""

usage = """Usage:

    csvgraph.py filename.csv "X column" "Y column 1" ["Y column 2"] ...

Where filename.csv contains comma-separated values, with column names in the
first row, and all subsequent arguments are regular expressions that may match
one or more column names.

At least one X-column and one Y-column must be provided; if any Y-column
expression matches multiple column names, and/or if multiple Y-column
expressions are provided, then all matching columns will be included in the
graph.

If the X-column is a date field, then the X axis will be displayed in HH:MM
format. Otherwise, all columns must be numeric (integer or floating-point).
"""

import csv
import sys
from datetime import datetime
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
        columns = [column for column in fieldnames if re.match(expr, column)]
        if columns:
            print("Expression: '%s' matched these columns:")
            print('\n'.join(columns))
            return columns
        else:
            raise NoMatch("No matching column found for '%s'" % expr)

    # Get the first matching X column, and all matching Y columns
    x_column = _matches(x_expr)[0]
    y_columns = sum([_matches(y_expr) for y_expr in y_exprs], [])

    return (x_column, y_columns)


# Main program
if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage_error("Need a filename and at least two column names")
    else:
        args = sys.argv[1:]

    csvfile = args.pop(0)
    x_expr = args.pop(0)
    y_exprs = args

    print("Reading '%s'" % csvfile)
    reader = csv.DictReader(open(csvfile, 'r'))

    # Attempt to match column names
    try:
        x_column, y_columns = match_columns(x_expr, y_exprs, reader.fieldnames)
    except NoMatch, err:
        usage_error(err)

    # Read each row in the .csv file and populate x and y value lists
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

    # Create the figure and plot
    figure = pylab.figure()
    axes = figure.add_subplot(111, xlabel=x_column)
    axes.grid(True)

    # Do date formatting if the X column was a date field
    if x_is_date:
        # Format the X-axis tick marks
        axes.xaxis.set_major_locator(dates.HourLocator())
        axes.xaxis.set_minor_locator(dates.MinuteLocator())
        axes.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        axes.set_xlim(min(x_values), max(x_values))

        # Adjust formatting and margin for date labels
        figure.autofmt_xdate()

    # Plot lines for all Y columns
    lines = []
    for y_col in y_columns:
        line = axes.plot(x_values, y_values[y_col])
        lines.append(line)

    # Draw a legend for the figure
    legend = figure.legend(lines, y_columns, 'upper right')
    legend.get_frame().set_alpha(0.5)

    # Show the graph viewer
    pylab.show()


