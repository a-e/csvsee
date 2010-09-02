# graph.py

"""Provides a `Graph` class for creating graphs from ``.csv`` data files.
"""

# TODO
# ----

# The graph legend looks terrible almost all the time. It does especially badly
# with really long column names, and more than about 6 columns.

# Possible solutions:
# - Truncate all column names so they will fit
# - Make larger graphs to ensure the legend won't overlap the graph
# - Write legend to a separate image


import sys
import csv
import re
from datetime import datetime, timedelta

from csvsee import utils


class NoMatch (Exception):
    """Exception raised when no column name matches a given expression."""
    pass


def runtime_error(message):
    """Print an error message, then exit.
    """
    print('*** Error: %s' % message)
    sys.exit(1)


def date_locator_formatter(min_date, max_date):
    """Determine suitable locator and format to use for a range of dates.
    Returns `(locator, formatter)` where `locator` is an `RRuleLocator`,
    and `formatter` is a `DateFormatter`.
    """
    from matplotlib import dates

    date_range = max_date - min_date
    # Use HH:MM format by default
    date_format = '%H:%M'

    # For more than 2 days, label each day
    if date_range > timedelta(days=2):
        locator = dates.DayLocator(interval=1)
        date_format = '%b %d'

    # For more than 24 hours, label every 6 hours
    elif date_range > timedelta(hours=24):
        locator = dates.HourLocator(interval=6)

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


def read_csv_values(reader, x_column, y_columns, date_format='', gmt_offset=0):
    """Read values from a csv `DictReader`, and return all values in
    `x_column` and `y_columns`.
    """
    x_values = []
    y_values = {}

    for row in reader:
        x_value = row[x_column]

        # If X is supposed to be a date, try to convert it
        if date_format:
            x_value = datetime.strptime(x_value, date_format) + \
                timedelta(hours=gmt_offset)
        # Otherwise, assume it's a floating-point numeric value
        else:
            x_value = utils.float_or_0(x_value)

        x_values.append(x_value)

        # Append Y values from each column
        for y_col in y_columns:
            if y_col not in y_values:
                y_values[y_col] = []
            y_values[y_col].append(utils.float_or_0(row[y_col]))

    return (x_values, y_values)


def top_by_average(n, y_columns, y_values):
    """Determine the top ``n`` columns based on the average of values
    in ``y_values``, and return the filtered ``y_columns`` names.
    """
    averages = []
    for column in y_columns:
        values = y_values[column]
        avg = sum(values) / len(values)
        averages.append((avg, column))
    # Keep the top n averages
    sorted_columns = [col for (avg, col) in reversed(sorted(averages))]
    return sorted_columns[0:n]


def top_by_peak(n, y_columns, y_values):
    """Determine the top ``n`` columns based on the peak value
    in ``y_values``, and return the filtered ``y_columns`` names.
    """
    peaks = []
    for column in y_columns:
        peak = max(y_values[column])
        peaks.append((peak, column))
    # Keep the top n peaks
    sorted_columns = [col for (peak, col) in reversed(sorted(peaks))]
    return sorted_columns[0:n]


class Graph (object):
    """A graph of data from a CSV file.
    """
    def __init__(self, csv_file, x_expr='', y_exprs=['.*'], title='',
                 date_format='guess', line_style=''):
        """Create a graph from `csvfile`, with `x_expr` defining the x-axis,
        and `y_exprs` being columns to get y-values from.
        """
        self.csv_file = csv_file
        self.x_expr = x_expr
        self.y_exprs = y_exprs
        self.title = title or csv_file
        self.date_format = date_format
        self.line_style = line_style
        self.gmt_offset = 0
        self.xlabel = ''
        self.ylabel = ''
        self.ymax = 0
        self.truncate = 0
        self.top = 0
        self.peak = 0
        # These will be set by generate()
        self.figure = None
        self.figtitle = None
        self.axes = None
        self.legend = None


    def guess_date_format(self, date_column):
        """Try to guess the date format used in the current .csv file, by
        reading ``date_column`` from the first row.
        """
        infile = open(self.csv_file, 'r')
        reader = csv.DictReader(infile)
        row = reader.next()
        infile.close()
        # Return the guessed format
        return utils.guess_date_format(row[date_column])


    def generate(self):
        """Generate the graph.
        """
        import pylab

        print("Reading '%s'" % self.csv_file)
        reader = csv.DictReader(open(self.csv_file, 'r'))

        # Attempt to match column names
        try:
            x_column, y_columns = self.match_columns(reader.fieldnames)
        except NoMatch as err:
            runtime_error(err)

        # Do we need to guess what format the date is in?
        if self.date_format == 'guess':
            self.date_format = self.guess_date_format(x_column)

        # Read each row in the .csv file and populate x and y value lists
        x_values, y_values = read_csv_values(reader,
            x_column, y_columns, self.date_format, self.gmt_offset)

        # Create the figure and plot
        self.figure = pylab.figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.grid(True)

        # Label X-axis with provided label, or column name
        self.axes.set_xlabel(self.xlabel or x_column)

        # Add graph title if provided
        if self.title:
            self.figtitle = self.figure.suptitle(self.title, fontsize=18)

        # Do date formatting of axis labels if the X column is a date field
        if self.date_format:
            self.add_date_labels(min(x_values), max(x_values))
            self.figure.autofmt_xdate()

        # Get the top n by average?
        if self.top:
            y_columns = top_by_average(self.top, y_columns, y_values)
            print("********** Top %d columns by average:" % self.top)
            print('\n'.join(y_columns))
        # Get the top n by peak?
        elif self.peak:
            y_columns = top_by_peak(self.peak, y_columns, y_values)
            print("********** Top %d columns by peak:" % self.peak)
            print('\n'.join(y_columns))

        # Plot lines for all Y columns
        lines = []
        for y_col in y_columns:
            line = self.axes.plot(x_values, y_values[y_col], self.line_style)
            lines.append(line)

        # Set Y-limit if provided
        if self.ymax > 0:
            print("Setting ymax to %s" % self.ymax)
            self.axes.set_ylim(0, self.ymax)

        # Draw a legend for the figure
        # If a Y label was given, use that; otherwise, strip
        # common prefix from labels, and use that as the Y label
        if self.ylabel:
            labels = [col for col in y_columns]
            self.axes.set_ylabel(self.ylabel)
        else:
            prefix, labels = utils.strip_prefix(y_columns)
            self.axes.set_ylabel(prefix)

        # Truncate labels if desired
        if self.truncate > 0:
            labels = [label[0:self.truncate] for label in labels]

        self.legend = pylab.legend(lines, labels,
            loc='upper center', bbox_to_anchor=(0.5, -0.15),
            prop={'size': 9}, ncol=3)


    def match_columns(self, fieldnames):
        """Match `x_expr` and `y_exprs` to all available column
        names in `fieldnames`. Return the matched `x_column` and
        `y_columns`. If no matches are found for any expression,
        raise a `NoMatch` exception.
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
        if self.x_expr:
            x_column = _matches(self.x_expr, fieldnames)[0]
        # Otherwise, just take the first field.
        else:
            x_column = fieldnames[0]

        # In any case, remove the x column from fieldnames so it
        # won't be matched by any y-expression.
        fieldnames.remove(x_column)

        # Get all matching Y columns
        y_columns = sum([_matches(y_expr, fieldnames)
                         for y_expr in self.y_exprs],
                        [])

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
        # Ensure that title and legend don't get cropped out
        extra = [
            self.legend.legendPatch,
            self.figtitle,
        ]
        self.figure.savefig(
            filename,
            format=ext,
            bbox_inches='tight',
            bbox_extra_artists=extra)
        print("Saved '%s' in '%s' format." % (filename, ext))

    def show(self):
        """Display the graph in a GUI window.
        """
        import pylab
        pylab.show()


