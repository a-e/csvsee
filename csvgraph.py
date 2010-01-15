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

    -title "Title"
        Set the title label for the graph. Default: No title.
    -save "filename.(png|svg|pdf)"
        Save the graph to a file. Default: Show the graph in a viewer.
    -dateformat "<format string>"
        Interpret the X-column as a date in the given format. Examples:
            %m/%d/%y %I:%M:%S %p: 12/10/09 3:45:56 PM (Grinder logs)
            %m/%d/%Y %H:%M:%S.%f: 12/10/2009 15:45:56.789 (Perfmon)
        See http://docs.python.org/library/datetime.html for valid formats.
        The Perfmon date format is the default. If the X-column
        is NOT a date, use -dateformat ""
    -linestyle "<format string>"
        Define the style of lines plotted on the graph. Examples are:
            "-"  Solid line (Default)
            "."  Point marker
            "o"  Circle marker
            "o-" Circle + solid lines
        See the Matplotlib Axes.plot documentation for available styles:
        http://matplotlib.sourceforge.net/api/axes_api.html#matplotlib.axes.Axes.plot

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
    print('*** %s' % message)
    sys.exit(1)


def runtime_error(message):
    """Print an error message, then exit.
    """
    print('*** Error: %s' % message)
    sys.exit(1)


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
    date_format = '%H:%M'

    # If date range is more than 2 days, label each day
    if date_range > timedelta(days=2):
        axes.xaxis.set_major_locator(dates.HourLocator(interval=24))
        date_format = '%b %d'

    # If date range is more than 24 hours, label every 12 hours
    elif date_range > timedelta(hours=24):
        axes.xaxis.set_major_locator(dates.HourLocator(interval=12))

    # If date range is more than 2 hours, label every 30 minutes
    elif date_range > timedelta(hours=2):
        axes.xaxis.set_major_locator(dates.MinuteLocator(interval=30))

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
    axes.xaxis.set_major_formatter(dates.DateFormatter(date_format))


def read_csv_values(reader, x_column, y_columns, date_format=''):
    """Read values from a csv `DictReader`, and return all values in
    `x_column` and `y_columns`.
    """
    x_values = []
    y_values = {}
    for row in reader:
        x_value = row[x_column]
        if date_format:
            x_value = datetime.strptime(x_value, date_format)
        else:
            x_value = float_or_0(x_value)

        x_values.append(x_value)

        # Append Y values from each column
        for y_col in y_columns:
            if y_col not in y_values:
                y_values[y_col] = []
            y_values[y_col].append(float_or_0(row[y_col]))

    return x_values, y_values


def add_notes(figure, axes, notes_file):
    # Draw a vertical line
    annot_lines = [
        axes.axvline(x_values[4]),
        axes.axvline(x_values[8]),
    ]
    annot_labels = [
        'Hello world',
        'Goodbye cruel world',
    ]
    annot_legend = figure.legend(annot_lines, annot_labels,
        prop={'size': 9})


def do_graph(csvfile, x_expr, y_exprs, title='', save_file='',
    date_format='', line_style='-'):
    """Generate a graph from `csvfile`, with `x_expr` defining the x-axis,
    and `y_exprs` being columns to get y-values from.
    """
    print("Reading '%s'" % csvfile)
    reader = csv.DictReader(open(csvfile, 'r'))

    # Attempt to match column names
    try:
        x_column, y_columns = match_columns(x_expr, y_exprs, reader.fieldnames)
    except NoMatch as err:
        runtime_error(err)

    # Confirm with the user
    answer = raw_input("Graph these %d columns? " % len(y_columns))
    if answer.lower() != 'y':
        print("Quitting.")
        sys.exit(0)

    # Read each row in the .csv file and populate x and y value lists
    x_values, y_values = read_csv_values(reader,
        x_column, y_columns, date_format)

    # Create the figure and plot
    figure = pylab.figure()
    axes = figure.add_subplot(111, xlabel=x_column)
    axes.grid(True)

    if title:
        figure.suptitle(title, fontsize=18)

    # Do date formatting if the X column was a date field
    if date_format:
        min_date, max_date = min(x_values), max(x_values)
        add_date_labels(axes, min_date, max_date)
        figure.autofmt_xdate()

    # Plot lines for all Y columns
    lines = []
    for y_col in y_columns:
        line = axes.plot(x_values, y_values[y_col], line_style)
        lines.append(line)

    # Add annotations if filename was provided (not implemented yet)
    #if notes_file:
    #    add_notes(figure, axes, notes_file)

    # Draw a legend for the figure
    short_labels = shorten_labels(y_columns)
    legend = figure.legend(lines, short_labels, 'lower center',
        prop={'size': 9}, ncol=3)

    # If save_file was provided, write output to the given filename
    if save_file:
        ext = save_file[-3:]
        if ext not in ('png',  'svg', 'pdf'):
            print("File extension '%s' unknown. Assuming 'png'." % ext)
            ext = 'png'
        figure.savefig(save_file, format=ext)
        print("Saved '%s' in '%s' format." % (save_file, ext))
    # Otherwise, just show the graph viewer
    else:
        pylab.show()


def shorten_labels(labels):
    """Given a list of column labels of the form "\A\B\C", return
    a new list of labels with any common A, B, C parts.
    """
    # Don't try to shorten fewer than 2 labels
    if len(labels) < 2:
        return labels
    split_labels = (label.split('\\') for label in labels)
    transposed = zip(*split_labels)
    while len(set(transposed[0])) == 1:
        transposed.pop(0)
    return ['\\'.join(parts) for parts in zip(*transposed)]


# Main program
if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage_error("Need a filename and at least two column names")
    else:
        args = sys.argv[1:]

    title = ''
    save_file = ''
    date_format = '%m/%d/%Y %H:%M:%S.%f' # Perfmon format

    # Get -options
    while args[0].startswith('-'):
        opt = args.pop(0)
        if opt == '-title':
            title = args.pop(0)
        elif opt == '-save':
            save_file = args.pop(0)
        elif opt == '-dateformat':
            date_format = args.pop(0)
        elif opt == '-linestyle':
            line_style = args.pop(0)
        else:
            usage_error("Unknown option: %s" % arg)

    # Get positional arguments
    csvfile = args.pop(0)
    x_expr = args.pop(0)
    y_exprs = args

    # Generate the graph
    do_graph(csvfile, x_expr, y_exprs, title, save_file, date_format, line_style)


