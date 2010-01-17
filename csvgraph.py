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
import re
from datetime import datetime, timedelta
import pylab
from matplotlib import dates


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
    """Try to convert `value` to a floating-point number. If
    conversion fails, return 0.
    """
    try:
        return float(value)
    except ValueError:
        return 0


def strip_prefix(strings):
    """Strip a common prefix from a sequence of strings.
    Return `(prefix, stripped)` where `prefix` is the string that
    is common, and `stripped` is strings with the prefix removed.
    """
    prefix = ''
    # Group all first letters, then all second letters, etc.
    # letters list will be the same length as the shortest label
    for letters in zip(*strings):
        # If all letters are the same, append to common prefix
        if len(set(letters)) == 1:
            prefix += letters[0]
    index = len(prefix)
    stripped = [s[index:] for s in strings]
    return (prefix, stripped)


def date_locator_formatter(min_date, max_date):
    """Determine suitable locator and format to use for a range of dates.
    Returns `(locator, formatter)` where `locator` is an `RRuleLocator`,
    and `formatter` is a `DateFormatter`.
    """
    date_range = max_date - min_date
    # Use HH:MM format by default
    date_format = '%H:%M'

    # For more than 2 days, label each day
    if date_range > timedelta(days=2):
        locator = dates.DayLocator(interval=1)
        date_format = '%b %d'

    # For more than 24 hours, label every 12 hours
    elif date_range > timedelta(hours=24):
        locator = dates.HourLocator(interval=12)

    # For more than 2 hours, label every hour
    elif date_range > timedelta(hours=2):
        locator = dates.HourLocator(interval=1)

    # For more than 30 minutes, label 10-minute increments
    elif date_range > timedelta(minutes=30):
        locator = dates.MinuteLocator(interval=10)

    # For more than 10 minutes, label every 5 minutes
    elif date_range > timedelta(minutes=10):
        locator = dates.MinuteLocator(interval=5)

    # For 10 minutes or less, label every minute
    else:
        locator = dates.MinuteLocator()

    formatter = dates.DateFormatter(date_format)
    return (locator, formatter)

def read_csv_values(reader, x_column, y_columns, date_format=''):
    """Read values from a csv `DictReader`, and return all values in
    `x_column` and `y_columns`.
    """
    x_values = []
    y_values = {}
    for row in reader:
        x_value = row[x_column]

        # If X is supposed to be a date, try to convert it
        if date_format:
            x_value = datetime.strptime(x_value, date_format)
        # Otherwise, assume it's a floating-point numeric value
        else:
            x_value = float_or_0(x_value)

        x_values.append(x_value)

        # Append Y values from each column
        for y_col in y_columns:
            if y_col not in y_values:
                y_values[y_col] = []
            y_values[y_col].append(float_or_0(row[y_col]))

    return (x_values, y_values)


class Graph (object):
    """A graph of data from a CSV file.
    """
    def __init__(self, csv_file, x_expr, y_exprs, title='', date_format='', line_style=''):
        """Create a graph from `csvfile`, with `x_expr` defining the x-axis,
        and `y_exprs` being columns to get y-values from.
        """
        self.csv_file = csv_file
        self.x_expr = x_expr
        self.y_exprs = y_exprs
        self.title = title
        self.date_format = date_format
        self.line_style = line_style


    def generate(self):
        """Generate the graph.
        """
        print("Reading '%s'" % csvfile)
        reader = csv.DictReader(open(self.csv_file, 'r'))

        # Attempt to match column names
        try:
            x_column, y_columns = self.match_columns(reader.fieldnames)
        except NoMatch as err:
            runtime_error(err)

        # Read each row in the .csv file and populate x and y value lists
        x_values, y_values = read_csv_values(reader,
            x_column, y_columns, self.date_format)

        # Create the figure and plot
        self.figure = pylab.figure()
        self.axes = self.figure.add_subplot(111, xlabel=x_column)
        self.axes.grid(True)

        # Add graph title if provided
        if self.title:
            self.figure.suptitle(self.title, fontsize=18)

        # Do date formatting if the X column is a date field
        if self.date_format:
            self.add_date_labels(min(x_values), max(x_values))
            self.figure.autofmt_xdate()

        # Plot lines for all Y columns
        lines = []
        for y_col in y_columns:
            line = self.axes.plot(x_values, y_values[y_col], self.line_style)
            lines.append(line)

        # Draw a legend for the figure
        # Strip common prefix from labels, and use as legend title
        prefix, labels = strip_prefix(y_columns)
        self.legend = self.figure.legend(lines, labels, 'lower center',
            prop={'size': 9}, ncol=3, title=prefix)

    def match_columns(self, fieldnames):
        """Match `x_expr` and `y_exprs` to all available column
        names in `fieldnames`. Return the matched `x_column` and
        `y_columns`. If no matches are found for any expression,
        raise a `NoMatch` exception.
        """
        def _matches(expr):
            """Return a list of matching column names for `expr`,
            or raise a `NoMatch` exception if there were none.
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
        x_column = _matches(self.x_expr)[0]
        y_columns = sum([_matches(y_expr) for y_expr in self.y_exprs], [])

        return (x_column, y_columns)

    def add_date_labels(self, min_date, max_date):
        """Add date labels to the graph.
        """
        self.axes.set_xlim(min_date, max_date)
        locator, formatter = date_locator_formatter(min_date, max_date)
        self.axes.xaxis.set_major_locator(locator)
        self.axes.xaxis.set_major_formatter(formatter)

    def save(self, filename):
        """Save the graph to a .png, .svg, or .pdf file.
        """
        ext = filename[-3:]
        if ext not in ('png',  'svg', 'pdf'):
            print("File extension '%s' unknown. Assuming 'png'." % ext)
            ext = 'png'
        self.figure.savefig(filename, format=ext)
        print("Saved '%s' in '%s' format." % (filename, ext))

    def show(self):
        """Display the graph in a GUI window.
        """
        pylab.show()



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



# Main program
if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage_error("Need a filename and at least two column names")
    else:
        args = sys.argv[1:]

    title = ''
    save_file = ''
    date_format = '%m/%d/%Y %H:%M:%S.%f' # Perfmon format
    line_style = '-'

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
            usage_error("Unknown option: %s" % opt)

    # Get positional arguments
    csvfile = args.pop(0)
    x_expr = args.pop(0)
    y_exprs = args

    # Generate the graph
    #do_graph(csvfile, x_expr, y_exprs, title, save_file, date_format, line_style)
    graph = Graph(csvfile, x_expr, y_exprs, title, date_format, line_style)
    graph.generate()
    if save_file:
        graph.save(save_file)
    else:
        graph.show()




